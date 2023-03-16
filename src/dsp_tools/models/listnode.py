import json
from pprint import pprint
from typing import List, Optional, Any, Union
from urllib.parse import quote_plus


from dsp_tools.models.set_encoder import SetEncoder
from dsp_tools.models.connection import Connection
from dsp_tools.models.helpers import Actions
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.langstring import Languages, LangString
from dsp_tools.models.model import Model
from dsp_tools.models.project import Project

"""
This module implements the handling (CRUD) of list nodes and adds some function to read whole lists.

CREATE:
    * Instantiate a new object of the class ListNode
    * Call the ``create`` method on the instance

READ:
    * Instantiate a new object with ``id`` (IRI of listnode)
    * Call the ``read`` method on the instance
    * Access information about the instance

UPDATE:
    * Only partially implemented. Only "label" and "comment" attributes may be changed.
    * You need an instance of an existing ListNode by reading an instance
    * Change the attributes by assigning the new values
    * Call the ``update`` method on the instance

DELETE
    * NOT YET IMPLEMENTED!
"""


def list_creator(con: Connection,
                 project: Project,
                 parent_node: 'ListNode',
                 nodes: list[dict]) -> list['ListNode']:
    nodelist: list[ListNode] = []

    for node in nodes:
        new_node = ListNode(
            con=con,
            project=project,
            label=node["labels"],
            comments=node.get("comments"),
            name=node["name"],
            parent=parent_node
        )

        if node.get('nodes'):
            new_node.children = list_creator(con, project, new_node, node['nodes'])

        nodelist.append(new_node)

    return nodelist


class ListNode(Model):
    """
    This class represents a list node

    Attributes
    ----------

    con : Connection
        A Connection instance to a DSP server (for some operation a login has to be performed with valid credentials)

    id : str
        IRI of the list node [readonly, cannot be modified after creation of instance]

    project : str
        IRI of project. Only used for the creation of a new list (root node) [write].

    label : LangString
        A LangString instance with language dependent labels. Setting this attribute overwrites all entries
        with the new ones. In order to add/remove a specific entry, use "addLabel" or "rmLabel".
        At least one label is required [read/write].

    comments : LangString
        A LangString instance with language dependent comments. Setting this attributes overwrites all entries
        with the new ones. In order to add/remove a specific entry, use "addComment" or "rmComment".

    name : str
        A unique name for the ListNode (unique inside this list) [read/write].

    parent : IRI | ListNode
        Is required and allowed only for the CREATE operation. Otherwise use the
        "children" attribute [write].

    isRootNode : bool
        Is True if the ListNode is the root node of a list. Cannot be set [read].

    children : list[ListNode]
        Contains a list of child nodes. This attribute is only available for nodes that have been read by the
        method "getAllNodes()" [read].

    rootNodeIri : str
        IRI of the root node. This attribute is only available for nodes that have been read by the
        method "getAllNodes()" [read].

    Methods
    -------

    create : ListNode information object
        Creates a new list (node) and returns the information from the list (node). Use it to create new lists
        or append new ListNodes to an existing list.

    read : ListNode information object
        Returns information about a single list node

    update : ListNode information object
        Updates the changed attributes and returns the updated information from the ListNode

    delete :
        NOT YET IMPLEMENTED

    getAllNodes : ListNode
        Get all nodes of a list. The IRI of the root node has to be supplied.

    getAllLists [static]:
        Returns all lists of a project.

    print : None
        Prints the ListNode information to stdout (not recursive)

    """

    ROUTE = "/admin/lists"
    ROUTE_SLASH = ROUTE + "/"

    _id: Optional[str]
    _project: Optional[str]
    _label: Optional[LangString]
    _comments: Optional[LangString]
    _name: Optional[str]
    _parent: Optional[str]
    _isRootNode: bool
    _children: Optional[list['ListNode']]
    _rootNodeIri: Optional[str]

    def __init__(self,
                 con: Connection,
                 id: Optional[str] = None,
                 project: Optional[Union[Project, str]] = None,
                 label: LangString = None,
                 comments: Optional[LangString] = None,
                 name: Optional[str] = None,
                 parent: Optional[Union['ListNode', str]] = None,
                 isRootNode: bool = False,
                 children: Optional[list['ListNode']] = None,
                 rootNodeIri: Optional[str] = None):
        """
        This is the constructor for the ListNode object. For

        CREATE:
            * The "con" and at least one "label" are required
        READ:
            * The "con" and "id" attributes are required
        UPDATE:
            * Only "label", "comments" and "name" may be changed
        DELETE:
            * Not yet implemented

        :param con: A valid Connection instance with a user logged in that has the appropriate permissions
        :param id: IRI of the project [readonly, cannot be modified after creation of instance]
        :param project: IRI of project. Only used for the creation of a new list (root node) [write].
        :param label: A LangString instance with language dependent labels. Setting this attributes overwites all entries with the new ones. In order to add/remove a specific entry, use "addLabel" or "rmLabel". At least one label is required [read/write].
        :param comments: A LangString instance with language dependent comments. Setting this attributes overwites all entries with the new ones.In order to add/remove a specific entry, use "addComment" or "rmComment".
        :param name: A unique name for the ListNode (unique regarding the whole list) [read/write].
        :param parent: Is required and allowed only for the CREATE operation. Otherwise use the "children" attribute [write].
        :param isRootNode: Is True if the ListNode is a root node of a list Cannot be set [read].
        :param children: Contains a list of children nodes. This attribute is only available for nodes that have been read by the method "getAllNodes()"! [read]
        :param rootNodeIri: IRI of the root node. This attribute is only available for nodes that have been read by the method "getAllNodes()"! [read]
        """

        super().__init__(con)

        self._project = project.id if isinstance(project, Project) else str(project) if project else None
        self._id = str(id) if id else None
        self._label = LangString(label)
        self._comments = LangString(comments) if comments else None
        self._name = str(name) if name else None
        if parent and isinstance(parent, ListNode):
            self._parent = parent.id
        else:
            self._parent = str(parent) if parent else None
        self._isRootNode = isRootNode
        if children:
            if isinstance(children, List) and len(children) > 0 and isinstance(children[0], ListNode):
                self._children = children
            else:
                raise BaseError('ERROR Children must be list of ListNodes!')
        else:
            self._children = None
        if not isinstance(rootNodeIri, str) and rootNodeIri:
            raise BaseError('ERROR rootNodeIri must be of type string')
        self._rootNodeIri = rootNodeIri

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('ListNode id cannot be modified!')

    @property
    def project(self) -> Optional[str]:
        return self._project

    @project.setter
    def project(self, value: str) -> None:
        if self._project:
            raise BaseError('Project id cannot be modified!')
        else:
            self._project = value

    @property
    def label(self) -> Optional[LangString]:
        return self._label

    @label.setter
    def label(self, value: Optional[Union[LangString, str]]) -> None:
        self._label = LangString(value)
        self._changed.add('label')

    def addLabel(self, lang: Union[Languages, str], value: str) -> None:
        """
        Add/replace a node label with the given language (executed at next update)

        :param lang: The language the label, either a string "EN", "DE", "FR", "IT" or a Language instance
        :param value: The text of the label
        :return: None
        """

        self._label[lang] = value
        self._changed.add('label')

    def rmLabel(self, lang: Union[Languages, str]) -> None:
        """
        Remove a label from a list node (executed at next update)

        :param lang: The language the label to be removed is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :return: None
        """
        del self._label[lang]
        self._changed.add('label')

    @property
    def comments(self) -> Optional[LangString]:
        return self._comments

    @comments.setter
    def comments(self, value: Optional[Union[LangString, str]]) -> None:
        self._comments = LangString(value)
        self._changed.add('comments')

    def addComment(self, lang: Union[Languages, str], value: str) -> None:
        """
        Add/replace a node comments with the given language (executed at next update)

        :param lang: The language the comments, either a string "EN", "DE", "FR", "IT" or a Language instance
        :param value: The text of the comments
        :return: None
        """

        self._comments[lang] = value
        self._changed.add('comments')

    def rmComment(self, lang: Union[Languages, str]) -> None:
        """
        Remove a comments from a list node (executed at next update)

        :param lang: The language the comment to be removed is in, either a string "EN", "DE", "FR", "IT" or a Language instance
        :return: None
        """
        del self._comments[lang]
        self._changed.add('comments')

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = str(value)
        self._changed.add('name')

    @property
    def parent(self) -> Optional[str]:
        return self._parent if self._parent else None

    @parent.setter
    def parent(self, value: Union[str, 'ListNode']):
        if isinstance(value, ListNode):
            self._parent = value.id
        else:
            self._parent = value

    @property
    def isRootNode(self) -> Optional[bool]:
        return self._isRootNode

    @isRootNode.setter
    def isRootNode(self, value: bool) -> None:
        raise BaseError('Property isRootNode cannot be set!')

    @property
    def children(self) -> Optional[list['ListNode']]:
        return self._children

    @children.setter
    def children(self, value: list['ListNode']) -> None:
        self._children = value

    @staticmethod
    def __getChildren(con: Connection,
                      parent_iri: str,
                      project_iri: str,
                      children: list[Any]) -> Optional[list['ListNode']]:
        """
        Internal method! Should not be used directly!

        Static method gets a recursive List of children nodes

        :param con: Valid Connection instance
        :param children: json object of children
        :return: List of ListNode instances
        """
        if children:
            child_nodes: list[Any] = []
            for child in children:

                if 'parentNodeIri' not in child:
                    child['parentNodeIri'] = parent_iri
                if 'projectIri' not in child:
                    child['projectIri'] = project_iri
                child_node = ListNode.fromJsonObj(con, child)
                child_nodes.append(child_node)
            return child_nodes
        else:
            return None

    @property
    def rootNodeIri(self) -> Optional[str]:
        return self._rootNodeIri

    @rootNodeIri.setter
    def rootNodeIri(self, value: str):
        raise BaseError('rootNodeIri cannot be set!')

    def has_changed(self) -> bool:
        if self._changed:
            return True
        else:
            return False

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> Any:
        """
        Internal method! Should not be used directly!

        This method is used to create a ListNode instance from the JSON data returned by DSP

        :param con: Connection instance
        :param json_obj: JSON data returned by DSP as python3 object
        :return: ListNode instance
        """

        id = json_obj.get('id')
        if id is None:
            raise BaseError('ListNode id is missing')
        project = json_obj.get('projectIri')
        label = LangString.fromJsonObj(json_obj.get('labels'))
        comments = LangString.fromJsonObj(json_obj.get('comments'))
        if json_obj.get('name'):
            name = json_obj['name']
        else:
            name = id.rsplit('/', 1)[-1]
        parent = json_obj.get('parentNodeIri')
        isRootNode = json_obj.get('isRootNode')

        child_info = json_obj.get('children')
        children = None
        if child_info:
            children = ListNode.__getChildren(con=con,
                                              parent_iri=id,
                                              project_iri=project,
                                              children=child_info)
        rootNodeIri = json_obj.get('hasRootNode')

        return cls(con=con,
                   id=id,
                   project=project,
                   label=label,
                   comments=comments,
                   name=name,
                   parent=parent,
                   isRootNode=isRootNode,
                   children=children,
                   rootNodeIri=rootNodeIri)

    def toJsonObj(self, action: Actions, listIri: str = None) -> Any:
        """
        Internal method! Should not be used directly!

        Creates a JSON-object from the ListNode instance that can be used to call DSP-API

        :param action: Action the object is used for (Action.CREATE or Action.UPDATE)
        :param listIri: The IRI of the list node, only used for update action
        :return: JSON-object

        """

        tmp = {}

        if action == Actions.Create:
            if self._project is None:
                raise BaseError("There must be a project id given!")
            tmp['projectIri'] = self._project
            if self._label.isEmpty():
                raise BaseError("There must be a valid ListNode label!")
            tmp['labels'] = self._label.toJsonObj()
            if self._comments:
                tmp['comments'] = self._comments.toJsonObj()
            if self._name:
                tmp['name'] = self._name
            if self._parent:
                tmp['parentNodeIri'] = self._parent

        elif action == Actions.Update:
            if self.id is None:
                raise BaseError("There must be a node id given!")
            tmp['listIri'] = listIri
            if self._project is None:
                raise BaseError("There must be a project id given!")
            tmp['projectIri'] = self._project
            if not self._label.isEmpty() and 'label' in self._changed:
                tmp['labels'] = self._label.toJsonObj()
            if not self._comments.isEmpty() and 'comments' in self._changed:
                tmp['comments'] = self._comments.toJsonObj()
            if self._name and 'name' in self._changed:
                tmp['name'] = self._name

        return tmp

    def create(self) -> 'ListNode':
        """
        Create a new List

        :return: JSON-object from DSP-API
        """

        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        if self._parent:
            result = self._con.post(ListNode.ROUTE_SLASH + quote_plus(self._parent), jsondata)
            return ListNode.fromJsonObj(self._con, result['nodeinfo'])
        else:
            result = self._con.post(ListNode.ROUTE, jsondata)
            return ListNode.fromJsonObj(self._con, result['list']['listinfo'])

    def read(self) -> Any:
        """
        Read a project from DSP-API

        :return: JSON-object from DSP-API
        """

        result = self._con.get(ListNode.ROUTE_SLASH + 'nodes/' + quote_plus(self._id))
        if result.get('nodeinfo'):
            return self.fromJsonObj(self._con, result['nodeinfo'])
        elif result.get('listinfo'):
            return self.fromJsonObj(self._con, result['listinfo'])
        else:
            return None

    def update(self) -> Union[Any, None]:
        """
        Update the ListNode info in DSP with the modified data in this ListNode instance

        :return: JSON-object from DSP-API reflecting the update
        """

        jsonobj = self.toJsonObj(Actions.Update, self.id)
        if jsonobj:
            jsondata = json.dumps(jsonobj, cls=SetEncoder)
            result = self._con.put(ListNode.ROUTE_SLASH + quote_plus(self.id), jsondata)
            pprint(result)
            return ListNode.fromJsonObj(self._con, result['listinfo'])
        else:
            return None

    def delete(self) -> None:
        """
        Delete the given ListNode

        :return: DSP-API response
        """
        raise BaseError("NOT YET IMPLEMENTED")
        result = self._con.delete(ListNode.ROUTE_SLASH + quote_plus(self._id))
        return result
        # return Project.fromJsonObj(self.con, result['project'])

    def getAllNodes(self) -> 'ListNode':
        """
        Get all nodes of the list. Must be called from a ListNode instance that has at least set the
        list iri!

        :return: Root node of list with recursive ListNodes ("children"-attributes)
        """

        result = self._con.get(ListNode.ROUTE_SLASH + quote_plus(self._id))
        if 'list' not in result:
            raise BaseError("Request got no list!")
        if 'listinfo' not in result['list']:
            raise BaseError("Request got no proper list information!")
        root = ListNode.fromJsonObj(self._con, result['list']['listinfo'])
        if 'children' in result['list']:
            root._children = ListNode.__getChildren(con=self._con,
                                                    parent_iri=root.id,
                                                    project_iri=root.project,
                                                    children=result['list']['children'])
        return root

    @staticmethod
    def getAllLists(con: Connection, project_iri: Optional[str] = None) -> list['ListNode']:
        """
        Get all lists. If a project IRI is given, it returns the lists of the specified project

        :param con: Connection instance
        :param project_iri: Iri/id of project
        :return: list of ListNodes
        """
        if project_iri is None:
            result = con.get(ListNode.ROUTE)
        else:
            result = con.get(ListNode.ROUTE + '?projectIri=' + quote_plus(project_iri))
        if 'lists' not in result:
            raise BaseError("Request got no lists!")
        return list(map(lambda a: ListNode.fromJsonObj(con, a), result['lists']))

    def _createDefinitionFileObj(self, children: list["ListNode"]):
        """
        Create an object that corresponds to the syntax of the input to "create_onto".
        Node: This method must be used only internally (for recursion)!!

        :param children: List of children nodes
        :return: A python object that can be jsonfied to correspond to the syntax of the input to "create_onto".
        """
        listnodeobjs = []
        for listnode in children:
            listnodeobj = {
                "name": listnode.name,
                "labels": listnode.label.createDefinitionFileObj(),
            }
            if not listnode.comments.isEmpty():
                listnodeobj["comments"] = listnode.comments.createDefinitionFileObj()
            if listnode.children:
                listnodeobj["nodes"] = self._createDefinitionFileObj(listnode.children)
            listnodeobjs.append(listnodeobj)
        return listnodeobjs

    @staticmethod
    def readDefinitionFileObj(con: Connection, project: Project, rootnode: Any) -> 'ListNode':
        """
        Reads a JSON obj that corresponds to the syntax of the input to "create_onto".

        :param self:
        :param con: Connection object
        :param project: Project instance
        :param rootnode: root node of the list
        :return: an instance of ListNode corresponding to the root node
        """
        root_list_node = ListNode(
            con=con,
            project=project,
            label=rootnode['labels'],
            comments=rootnode.get('comments'),
            name=rootnode['name']
        )
        listnodes = list_creator(con, project, root_list_node, rootnode.get('nodes'))
        root_list_node.children = listnodes
        return root_list_node

    def createDefinitionFileObj(self):
        """
        Create an object that corresponds to the syntax of the input to "create_onto".
        :return: A python object that can be jsonfied to correspond to the syntax of the input to "create_onto".
        """
        listnode = {
            "name": self._name,
            "labels": self._label.createDefinitionFileObj(),
        }
        if not self._comments.isEmpty():
            listnode["comments"] = self._comments.createDefinitionFileObj()
        if self._children:
            listnode["nodes"] = self._createDefinitionFileObj(self._children)
        return listnode

    def print(self):
        """
        print info to stdout

        :return: None
        """

        print('Node Info:')
        print('  Id:        {}'.format(self._id))
        print('  Project:   {}'.format(self._project))
        print('  Name:      {}'.format(self._name))
        print('  Label:     ')
        if self._label:
            for lbl in self._label.items():
                print('             {}: {}'.format(lbl[0], lbl[1]))
        else:
            print('             None')
        print('  Comments:   ')
        if self._comments.isEmpty():
            for lbl in self._comments.items():
                print('             {}: {}'.format(lbl[0], lbl[1]))
        else:
            print('             None')
        print('  Parent', self._parent)
        print('  IsRootNode: {}'.format(self._isRootNode))