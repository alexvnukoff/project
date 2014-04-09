from django.db import models
from django.db import connection
from django.db.models import Q

class hierarchyManager(models.Manager):
    '''
        Hierarchy manager class
    '''

    #query skeleton
    query = '''SELECT  {select}
                            FROM
                            (
                                SELECT parent_id, child_id, type
                                    FROM {relTable}
                                UNION
                                    SELECT NULL, {pkCol}, null
                                        FROM
                                        (
                                            SELECT NULL, {pkCol}, null
                                                FROM {itemTable} i
                                                {unionJoin}
                                                WHERE NOT EXISTS
                                                (
                                                    SELECT *
                                                        FROM {relTable}
                                                        WHERE child_id = i.{pkCol} AND type='hierarchy'
                                                ) {unionWhere}
                                        ) WHERE ROWNUM <= {limitRoot}
                            ) rel
                            INNER JOIN {itemTable} model ON (rel.CHILD_ID = model.{pkCol})
                            WHERE rel.type='hierarchy' OR rel.PARENT_ID is null {where}
                            CONNECT BY PRIOR  {prior}
                            START WITH {startWith}
                            {order};'''

    def _getQueryDict(self):
        '''
            Set default values to fill the skeleton
        '''
        queryDict = {}

        queryDict['itemTable'] = self.model._meta.db_table
        queryDict['relTable'] = 'core_relationship'
        queryDict['pkCol'] = self.model._meta.pk.column
        queryDict['select'] = 'PARENT_ID, LEVEL, model.{pkCol} as id'.format(pkCol=queryDict['pkCol'])
        queryDict['where'] = ''
        queryDict['order'] = 'ORDER BY ROWNUM '
        queryDict['unionWhere'] = ''
        queryDict['unionJoin'] = ''
        queryDict['limitRoot'] = '50'


        return queryDict

    def getTree(self, rootLimit=False, siteID = False):
        '''
            Returns hierarchical structure of some type of Item
            The method returns list of dictionaries that contains the id , level and the parent of each member
            also ordered in hierarchical order
                Example: Department.hierarchy.getTree() #Returns all root departments and its children
                Example: Department.hierarchy.getTree(5) #Returns the tree of first 5 parents

            It will works only for submodels of the Item model (Department, Company etc.)
        '''

        if self.model._meta.object_name is "Item":
            return {}

        cursor = connection.cursor()
        queryDict = self._getQueryDict()
        queryDict['select'] += ', CONNECT_BY_ISLEAF as isLeaf'
        queryDict['prior'] = 'rel.CHILD_ID = rel.PARENT_ID'
        queryDict['startWith'] = 'rel.PARENT_ID is NULL'


        if siteID:
            queryDict['unionJoin'] = 'INNER JOIN "CORE_ITEM_SITES" ON ( i.%s = "CORE_ITEM_SITES"."ITEM_ID")' \
                                        % self.model._meta.pk.column
            queryDict['unionWhere'] = ' AND "CORE_ITEM_SITES"."SITE_ID" = %s' % siteID


        if rootLimit is not False:
            int(rootLimit)
            rootLimit = str(rootLimit)
        else:
            rootLimit = 50

        queryDict['limitRoot'] = '%s'


        finalQuery = self.query.format(**queryDict)

        cursor.execute(finalQuery, [rootLimit])

        desc = cursor.description

        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

    def getDescedantsForList(self, startList):
        '''
            Returns hierarchical structure of Descendants of list of Items
            you should pass a list of Items
            The method returns list of dictionaries that contains the id , level and the parent of each member
            also ordered in hierarchical order
                Example: Department.hierarchy.getDescedantsForList(startList=[1,2,3])
                #Returns descendants of each Item(1,2,3)
        '''

        if not startList:
            return {}

        if not isinstance(startList, list):
            startList = [startList]

        cursor = connection.cursor()
        queryDict = self._getQueryDict()
        queryDict['select'] += ', CONNECT_BY_ISLEAF as isLeaf'
        queryDict['startWith'] = 'rel.CHILD_ID IN ({list})'.format(list=','.join(["%s"]*len(startList)))
        queryDict['prior'] = 'rel.CHILD_ID = rel.PARENT_ID'

        finalQuery = self.query.format(**queryDict)

        cursor.execute(finalQuery, startList)
        desc = cursor.description

        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

    def getChild(self, parent):
        '''
            Returns hierarchical children's instances of parent Item
            you should pass the parent PK to "parent" parameter
                Example: Item.hierarchy.getChildren(parent=1)
                #Returns children hierarchical related to the Company with pk = 1
        '''
        return self.model.objects.filter(c2p__parent_id=parent, c2p__type="hierarchy")

    def getDescendantCount(self, parent):
        '''
            Get count of descendants in hierarchy
            this method return an integer value
                Example: count = Item.getDescendantCount(parent=1)
                #Returns number of descendants hierarchical related tho the Item = 1
        '''
        cursor = connection.cursor()
        queryDict = self._getQueryDict()
        queryDict['select'] = 'COUNT(*)-1'
        queryDict['prior'] = 'rel.CHILD_ID = rel.PARENT_ID'
        queryDict['startWith'] = 'rel.CHILD_ID = %s'

        finalQuery = self.query.format(**queryDict)

        cursor.execute(finalQuery, [parent])

        return cursor.fetchone()[0]

    def getAncestors(self, descendant, includeSelf=False):
        '''
            Returns hierarchical ancestors of some Item
            The method returns list of ancestors that contains the id , level and the parent of each member
            also ordered in hierarchical order.
            You should pass the descendant PK to a "descendant" parameter
                Example: Department.hierarchy.getAncestors(parent=10) #Returns ancestors of the Department
            By default it will NOT include the department itself, but it can be changed by passing `True`
            to the "includeSelf" parameter.
        '''
        cursor = connection.cursor()
        resultDict = {}
        queryDict = self._getQueryDict()
        queryDict['select'] = 'PARENT_ID, MAX(LEVEL) OVER () + 1 - LEVEL AS rev_level , model.{pkCol} as id'\
                                .format(pkCol=queryDict['pkCol'])
        queryDict['prior'] = 'rel.PARENT_ID = rel.CHILD_ID'
        queryDict['startWith'] = 'rel.CHILD_ID = %s'
        queryDict['order'] = 'ORDER BY rev_level'

        finalQuery = self.query.format(**queryDict)

        cursor.execute(finalQuery, [descendant])

        desc = cursor.description

        results = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

        for result in results:

            if includeSelf is False and descendant == result['ID']:
                results.remove(result)
            else:
                result['LEVEL'] = result['REV_LEVEL']
                del result['REV_LEVEL']


        return results

    def getDescendants(self, parent, includeSelf=False):
        '''
            Returns hierarchical descendants of Item
            The method returns list of descendants that contains the id , level and the parent of each member
            also ordered in hierarchical order.
            You should pass the PK of the parent to the "parent" parameter.
                Example: Department.hierarchy.getAncestors(parent=1) #Returns descendants of the Department
            also you can pass "True" to the "includeSelf" then it will include the parent itself
        '''
        cursor = connection.cursor()
        queryDict = self._getQueryDict()
        queryDict['select'] = 'PARENT_ID, CHILD_ID, LEVEL, CONNECT_BY_ISLEAF as isLeaf, model.{pkCol} as id'\
                                .format(pkCol=queryDict['pkCol'])
        queryDict['prior'] = 'rel.CHILD_ID = rel.PARENT_ID'
        queryDict['startWith'] = 'rel.CHILD_ID = %s'

        finalQuery = self.query.format(**queryDict)

        cursor.execute(finalQuery, [parent])

        desc = cursor.description

        results = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

        if includeSelf is False:
            for result in results:
                if parent == result['ID']:
                    results.remove(result)

        return results

    def getParent(self, child):
        '''
            Returns instance of the hierarchical parent for some Item passed to "child" parameter
                Example: Department.hierarchy.getParent(child=5)
                #Returns instance of department which is hierarchical parent of the Department=5
        '''
        return self.model.objects.get(p2c__child_id=child, p2c__type="hierarchy")

    def deleteTree(self, parent):
        '''
            Used to call delete method to all hierarchical child of parents passed to argument "parent"
                Example: Item.hierarchy.deleteTree(6)

            IMPORTANT: should be called from Item
        '''

        if not issubclass(parent, int):
            raise ValueError('Parent should be item PK')

        if self.model.__name__ != 'Item':
            raise ValueError('Accepting only Item instances except child subclasses')

        descendants = [descendant['ID'] for descendant in self.getChild(parent)]

        instList = self.model.objects.filter(pk__in=descendants)

        for inst in instList:
            inst.delete()

    def getRootParents(self, limit=0, siteID=False):
        '''
            Returns limited number of instances of root parents for some Type of Item
            by default it not limit the number of root parents and will return all them
                Example: Companies.hierarchy.getRootParents(5)
                Example: Companies.hierarchy.getRootParents()
        '''

        limit = int(limit)

        filter = {}

        if siteID:
            filter['sites'] = siteID

        if limit < 1:
            return self.model.objects.filter(Q(Q(c2p__type="hierarchy"),c2p__parent_id__isnull=True), **filter)
        else:
            return \
                self.model.objects.filter(Q(Q(c2p__type="hierarchy"), c2p__parent_id__isnull=True), **filter)[:limit]



