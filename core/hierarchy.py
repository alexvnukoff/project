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
                                                WHERE NOT EXISTS
                                                (
                                                    SELECT *
                                                        FROM {relTable}
                                                        WHERE child_id = i.{pkCol} AND type='hier'
                                                )
                                        ) WHERE ROWNUM <= {limitRoot}
                            ) rel
                            INNER JOIN {itemTable} model ON (rel.CHILD_ID = model.{pkCol})
                            WHERE rel.type='hier' OR rel.PARENT_ID is null {where}
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
        queryDict['where'] = ''
        queryDict['order'] = 'ORDER BY ROWNUM '

        queryDict['limitRoot'] = '50'


        return queryDict

    def getTree(self, rootLimit=False):
        '''
            Returns hierarchical structure of some type of Item
            The method returns list of dictionaries that contains the id , level and the parent of each member
            also ordered in hierarchical order
                Example: Department.hierarchy.getTree() //Returns all root departments and its children

            It will works only for submodels of the Item model (Department, Company etc.)
        '''

        if self.model._meta.object_name is "Item":
            return {}

        cursor = connection.cursor()
        queryDict = self._getQueryDict()
        queryDict['select'] += ', CONNECT_BY_ISLEAF as isLeaf'
        queryDict['prior'] = 'rel.CHILD_ID = rel.PARENT_ID'
        queryDict['startWith'] = 'rel.PARENT_ID is NULL'


        if rootLimit is not False:
            int(rootLimit)

            queryDict['limitRoot'] = str(rootLimit)


        finalQuery = self.query.format(**queryDict)

        cursor.execute(finalQuery)

        desc = cursor.description

        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

    def getDescedantsForList(self, startList):
        '''
            Returns hierarchical structure of Descendants of list of Items
            you should pass a list of Primary Keys of Items
            The method returns list of dictionaries that contains the id , level and the parent of each member
            also ordered in hierarchical order
                Example: Department.hierarchy.getDescedantsForList(startList=[1,2,3])
                //Returns descendants of each Item(1,2,3)
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
            you should passthe parent Primary Key to parent parameter
                Example: Department.hierarchy.getChildren(1)
                //Returns instances of children departments hierarchical related to the company with pk = 1

                Example: Item.hierarchy.getChildren(parent=1)
                //Returns children instances of all types of Item hierarchical related to the company with pk = 1
        '''
        return self.model.objects.filter(c2p__parent_id=parent, c2p__type="hier")

    def getDescendantCount(self, parent):
        '''
            Get count of descendants in hierarchy
            this method return a integer value
                Example: count = Item.getDescendantCount(parent=1)
                //Returns number of descendants hierarchical related tho the Item = 1
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
            Returns hierarchical structure of some type of Item
            The method returns list of ancestors that contains the id , level and the parent of each member
            also ordered in hierarchical order
            You should pass the Primary Key of the descendant to a "descendant" parameter
                Example: Department.hierarchy.getAncestors(parent=10) //Returns ancestors of the Departments
            also you can pass "True" to the "includeSelf" then it will include itself
                Example: Department.hierarchy.getAncestors(descendant=10, includeSelf=True)
                //Returns ancestors of the Departments include itself
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
            Returns hierarchical structure of some type of Item
            The method returns list of descendants that contains the id , level and the parent of each member
            also ordered in hierarchical order
            You should pass the Primary Key of the parent to a "parent" parameter
                Example: Department.hierarchy.getAncestors(parent=1) //Returns descendants of the Departments
            also you can pass "True" to the "includeSelf" then it will include itself
                Example: Department.hierarchy.getAncestors(descendant=10, includeSelf=True)
                //Returns descendants of the Departments include itself
        '''
        cursor = connection.cursor()
        queryDict = self._getQueryDict()
        queryDict['select'] = 'PARENT_ID, CHILD_ID, LEVEL, CONNECT_BY_ISLEAF as isLeaf, model.{pkCol} as id'\
                                .format(pkCol=queryDict['pkCol'])
        queryDict['prior'] = 'rel.CHILD_ID = rel.PARENT_ID'
        queryDict['startWith'] = 'rel.CHILD_ID = %s'
        queryDict['order'] = 'ORDER BY LEVEL'

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
            Returns instance of the hierarchical parent of some hierarchical child passed to "child" parameter
                Example: Department.hierarchy.getParent(child=5)
                //Returns instance of department which is hierarchical parent of the Department=5
        '''
        return self.model.objects.get(p2c__child_id=child, p2c__type="hier")

    def deleteTree(self, parents):

        if not isinstance(parents, list) and isinstance(parents, int):
            parents = [parents]

        if self.model.__name__ != 'Item':
            raise ValueError

        descendants = [descendant['ID'] for descendant in self.getDescedantsForList(parents)]

        self.model.objects.filter(pk__in=descendants).delete()



    def getRootParents(self, limit=0):
        limit = int(limit)

        if limit < 1:
            return self.model.objects\
                .filter(Q(Q(c2p__type="hier") | Q(c2p__type__isnull=True),c2p__parent_id__isnull=True))
        else:
            return \
                self.model.objects \
                    .filter(Q(Q(c2p__type="hier") | Q(c2p__type__isnull=True),c2p__parent_id__isnull=True))[:limit]


