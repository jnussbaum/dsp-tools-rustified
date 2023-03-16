from typing import Any, Optional, Union

from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.listnode import ListNode
from dsp_tools.models.project import Project
from dsp_tools.utils.excel_to_json_lists import expand_lists_from_excel
from dsp_tools.utils.shared import parse_json_input
from dsp_tools.utils.project_validate import validate_project
from dsp_tools.utils.shared import login, try_network_action


def _create_list_node(
    con: Connection,
    project: Project,
    node: dict[str, Any],
    parent_node: Optional[ListNode] = None
) -> tuple[dict[str, Any], bool]:
    """
    Creates a list node on the DSP server, recursively scanning through all its subnodes, creating them as well.
    If a node cannot be created, an error message is printed, but the process continues.

    Args:
        con: connection to the DSP server
        project: project that holds the list where this node should be added to
        node: the node to be created
        parent_node: parent node of the node to be created (optional)

    Returns:
        Returns a tuple consisting of a dict and a bool. 
        The dict contains the IRIs of the created list nodes,
        nested according to their hierarchy structure,
        i.e. ``{nodename: {"id": IRI, "nodes": {...}}}``.
        The bool is True if all nodes could be created, 
        False if any node could not be created.
    """
    new_node = ListNode(
        con=con,
        project=project,
        label=node["labels"],
        comments=node.get("comments"),
        name=node["name"],
        parent=parent_node
    )
    try:
        new_node = try_network_action(
            action=lambda: new_node.create(),
            failure_msg=f"ERROR while trying to create list node '{node['name']}'."
        )
    except BaseError as err:
        print(err.message)
        return {}, False

    # if node has child nodes, call the method recursively
    if node.get("nodes"):
        overall_success = True
        subnode_list = []
        for subnode in node["nodes"]:
            created_subnode, success = _create_list_node(con=con, project=project, node=subnode, parent_node=new_node)
            subnode_list.append(created_subnode)
            if not success:
                overall_success = False
        return {new_node.name: {"id": new_node.id, "nodes": subnode_list}}, overall_success  # type: ignore
    else:
        return {new_node.name: {"id": new_node.id}}, True  # type: ignore


def create_lists_on_server(
    lists_to_create: list[dict[str, Any]],
    con: Connection,
    project_remote: Project
) -> tuple[dict[str, Any], bool]:
    """
    Creates the "lists" section of a JSON project definition on a DSP server.
    If a list with the same name is already existing in this project on the DSP server, this list is skipped.

    Args:
        lists_to_create: "lists" section of a JSON project definition
        con: connection to the DSP server
        project_remote: representation of the project on the DSP server

    Returns:
        tuple consisting of the IRIs of the list nodes and the success status (True if everything went well)
    """
    
    overall_success = True
    
    # retrieve existing lists
    try:
        existing_lists: list[ListNode] = try_network_action(
            action=lambda: ListNode.getAllLists(con=con, project_iri=project_remote.id),
            failure_msg="WARNING: Unable to retrieve existing lists on DSP server. Cannot check if your lists are already existing."
        )
    except BaseError as err:
        print(err.message)
        existing_lists = []
        overall_success = False
    
    current_project_lists: dict[str, Any] = {}
    for new_list in lists_to_create:
        # if list exists already, add it to "current_project_lists" (for later usage), then skip it
        existing_list = [x for x in existing_lists if x.project == project_remote.id and x.name == new_list["name"]]
        if existing_list:
            current_project_lists[existing_list[0].name] = {"id": existing_list[0].id, "nodes": new_list["nodes"]}  # type: ignore
            print(f"\tWARNING: List '{new_list['name']}' already exists on the DSP server. Skipping...")
            overall_success = False
            continue

        created_list, success = _create_list_node(con=con, project=project_remote, node=new_list)
        current_project_lists.update(created_list)
        if not success:
            overall_success = False
        print(f"\tCreated list '{new_list['name']}'.")
    
    return current_project_lists, overall_success


def create_lists(
    project_file_as_path_or_parsed: Union[str, dict[str, Any]],
    server: str,
    user: str,
    password: str,
    dump: bool = False
) -> tuple[dict[str, Any], bool]:
    """
    This method accepts a JSON project definition, 
    expands the Excel sheets referenced in its "lists" section,
    connects to a DSP server,
    and uploads the "lists" section to the server. 

    The project must already exist on the DSP server.
    If a list with the same name is already existing in this project on the DSP server, this list is skipped.

    Args:
        project_file_as_path_or_parsed: path to the JSON project definition, or parsed JSON object
        server: URL of the DSP server
        user: Username (e-mail) for the DSP server, must have the permissions to create a project
        password: Password of the user
        dump: if True, the request is dumped as JSON (used for testing)

    Raises:
        BaseError: 
           - if the input is invalid
           - if a problem occurred while trying to expand the Excel files
           - if the JSON file is invalid according to the schema
           - if the connection to the DSP server cannot be established
           - if the project cannot be read from the server

    Returns:
        Returns a tuple consisting of a dict and a bool. 
        The dict contains the IRIs of the created list nodes,
        nested according to their hierarchy structure,
        i.e. ``{nodename: {"id": IRI, "nodes": {...}}}``.
        If there are no lists in the project definition, 
        an empty dictionary is returned. 
        The bool indicates if everything went smoothly during the process. 
        If a warning or error occurred (e.g. one of the lists already exists, 
        or one of the nodes could not be created), 
        it is False.
    """
    overall_success = True

    project_definition = parse_json_input(project_file_as_path_or_parsed=project_file_as_path_or_parsed)
    if not project_definition.get("project", {}).get("lists"):
        return {}, True
    lists_to_create = expand_lists_from_excel(project_definition["project"]["lists"])
    project_definition["project"]["lists"] = lists_to_create
    validate_project(project_definition, expand_lists=False)
    print('JSON project file is syntactically correct and passed validation.')

    # connect to the DSP server
    con = login(server, user, password)
    if dump:
        con.start_logging()

    # retrieve the project
    project_local = Project(con=con, shortcode=project_definition["project"]["shortcode"])
    project_remote = try_network_action(
        action=lambda: project_local.read(),
        failure_msg="ERROR while trying to create the lists: Project couldn't be read from the DSP server."
    )

    # create new lists
    current_project_lists, success = create_lists_on_server(lists_to_create=lists_to_create, con=con, project_remote=project_remote)
    if not success:
        overall_success = False

    return current_project_lists, overall_success