from app.newlinks import newlinks
from flask import render_template, flash, redirect, session, g, request, url_for, abort, jsonify
from utils_crawler import *
from app.apigraphdb import *
from validations import Validate

##Usage: http://localhost:5000/newlinks/randomrandom/?_token=NexusToken
## http://localhost:5000/newlinks/randomrandom?_token=NexusToken
@newlinks.route('/randomrandom/')
def show():
    return jsonify({'message':'randomrandom success'}), 200
    ##The below can b removed: not needed at all, checked completely
    # resp = Response(response=jsonify({'message':'randomrandom'}),
    #     status=200,
    #     mimetype="application/json")
    # return(resp)

@newlinks.route('/')
def home():
    return jsonify({'message':'Token works!'}), 200


##Usage: http://localhost:5000/newlinks/createtask/?_token=NexusToken2&taskname=wow77
@newlinks.route('/createtask/', methods=['POST'])
def createTask():

    ##every one has a list of tokens
    ##use tokens to register tasks

    ##for a token --> dict of tasks
    ##for a task --> dict of props

    tokenid = request.args.get('_token')

    token_task_dict= session.get(tokenid,{})

    taskname = request.args.get('taskname',None)

    ##if no task name is given in request arguments
    if taskname is None:
        return jsonify({'message': 'createtask: Cannot create, no taskname given to create'}), 400

    old_task = token_task_dict.get(taskname, None)

    print old_task

    ##if task name already exists against the current token
    if old_task is not None:
        return jsonify({'message': 'createtask: task already exists'}), 400


    timenow = getTimeNow()

    to_save_dict = {}
    to_save_dict['_token'] = tokenid
    to_save_dict['taskname'] = taskname
    to_save_dict['starttime'] = timenow
    to_save_dict['status'] = 'Active'

    token_task_dict[taskname] = to_save_dict

    session[tokenid] = token_task_dict

    return jsonify(token_task_dict), 201


##Usage: http://localhost:5000/newlinks/getalltasks/?_token=NexusToken2
@newlinks.route('/getalltasks/', methods=['GET'])
def getAllTasks():

    tokenid = request.args.get('_token')

    token_task_dict= session.get(tokenid,None)

    ##if no task name is given in request arguments
    ##TODO: decide if 200 or 400 bad request or success
    if token_task_dict is None:
        return jsonify({'message': 'getalltasks: No task at all'}), 200

    return jsonify(token_task_dict), 200


def error_helper(message,statuscode):
    return jsonify({'message':message}), statuscode


##MAJOR TODO: refactor code for future
##TODO: aliases a required property in apis? decision to take.
##TODO: constraints on json, check if the relations are between correct entities,
## if the labels are correct, if the props are corrrect, atleast the relations between the labels we want
##check will help in curning the menance of hyperedge!
@newlinks.route('/pushlinked/', methods=['POST'])
def pushLinked():

    ##TODO: validate and push json load to task table

    print 'datttttttta'
    print request.data
    print 'jsonnnnnnnn'
    print request.json

    if not request.json: ##is a dict!!
        return error_helper("The request body does not have JSON Data",400)

    ##removed entities, rels alone can be pushed if previous ids known
    ##changed name to meta_desc
    required_master_props = ['taskid', 'userid', 'token']
    for prop in required_master_props:
        if not prop in request.json:
            return error_helper(str(prop)+"property not in json data", 400)

    # patch for one of these should be present but never none
    # relations can exist in isolation coz of entities that are already present in db
    oneofthese = ['entities','relations']
    flag = False
    for prop in oneofthese:
        if prop in request.json:
            flag = True
            break

    if not flag:
        return error_helper("neither entities nor relations in json data", 400)

    taskid = request.json['taskid']
    tokenid = request.json['token']
    userid = request.json['userid']


    ##XXX: validate these three varibales
    ##XXX: tken, userid, task all valid

    if not taskid.isdigit():
        return error_helper("taskid should be an integer", 400)

    # INFO: tokenid is just for initial validation, will not be saved
    # taskid and userid will be saved
    ##TODO: if the combination is valid
    ##else abort
    ##TODO: get fetchdate and source_url to entities, , 'fetchdate', 'sourceurls'


    ## MAJOR TODO!
    ## some props are interanally reserved crawl_en_id not allowed for nodes
    ## what about ternary relations?
    ##
    ## check for strings
    ## validation checks: if task exists,
    ## ids repeated in nodes in json and in actual
    ## ids repeated in relations
    ## source_urls known in particular format
    ## fetch date in format
    ## allowed labels
    ## props allowed
    ## values all in strings or particular format?
    ## apis to add a new property in allowed dict with its description?
    ## ids ints?
    ## check if nodeid already exists in temp graph db, or relid
    ## create indexes and contsraints will have to add an internal label and internal relation label

    ##MAJOR TODO what to do about metadata?
    ##"description": "Naveen Jindal Connections",
    ##"fetchdate": "01/01/2011",
    ##use this metadata


    ##entities must part in request json
    entities = []
    if 'entities' in request.json:
        entities = request.json['entities'] ##MAJOR TODO: change this to nodes

    ##can be there or can not be, in json
    relations = []
    if 'relations' in request.json:
        relations = request.json['relations']


    # this is for returning the json to the user!
    subgraph = {}

    ##no need to return back token to the user
    #subgraph['token'] = tokenid ##TODO: exatly this? _token! conflict?
    subgraph['userid'] = userid
    subgraph['taskid'] = taskid
    #subgraph['pushdate'] = getTimeNow()

    nodes = {}
    links = {}

    ##MAJOR TODO reserved keywords and required keywords list
    ##MAJOR TODO format and pattern against keywords with regex ??

    required_endict_props = ['labels','properties','id','fetchdate','sourceurl']
    reserved_en_props = ['crawl_en_id','resolvedWithUUID','taskname','token',
    '_token','workname','date','time','resolvedDate',
    'resolvedAgainst','verifiedBy','resolvedBy','verifiedDate','update',
    'lastUpdatedBy','lastUpdatedOn', '_crawl_en_id_','_token_','_taskname_',
    '_id_','_nodenumber_','taskid','_taskid_','verifiedby','_verifiedby_','verifydate',
    'pushdate','_pushedby_','uuid','_uuid_','labels','_labels_','tasktype','_tasktype_','relid','_relid_'] ##_nodeid_ is the node number along with _token_ and _taskname_ will help us in identifying the node! so do not worry!

    ## ALIASES CODE
    # required_en_props = ['name','aliases'] ##inside entity['properties']

    required_en_props = ['name'] ##inside entity['properties']


    validate = Validate() ##TODO: move all validations to this class afterwards

    for en in entities:

        if not 'id' in en:
            return error_helper('id required attribute missing for an entity', 400)


        #print entities[en]
        nodeid = en['id']

        for prop in required_endict_props:
            if not prop in en:
                msg = str(prop)+' required attribute missing for entity %s' %(nodeid)
                return error_helper(msg, 400)

        if not nodeid.isdigit():
            msg = 'entity id should be a number for entity id %s' %(nodeid)
            return error_helper(msg, 400)

        if nodeid in nodes:
            msg = 'id repeated under entities for entity id %s' %(nodeid)
            return error_helper(msg, 400)

        if not len(en['labels'])>0:
            msg = 'Labels list empty for an entity for entity id %s' %(nodeid)
            return error_helper(msg, 400)

        for prop in required_en_props:
            if (not prop in en['properties']) : ##patch for allowing hyperedgenode, checked doesnt affect anything else
                msg = '%s required property missing for an entity for entity id %s' %(prop, nodeid)
                return error_helper(msg, 400)

        ## ALIASES CODE
        # if not len(en['properties']['aliases'])>0:
        #     return error_helper('aliases list empty for an entity', 400)
        # ##TODO: how to verify if the name is in aliases?

        ## XXX: aliases to be handled as a csv?? ##keep it as it is will add - will have to change code when generating keywords etc.
        ## Merge two options for all strings- assume csv seperate - add with "" and then see if lists do not have duplicates append and use
        ## aliases not a list many changes, many places! ##or you can just assume a list and assume no prop named aliases

        for prop in reserved_en_props:
            if prop in en['properties']:
                msg = str(prop)+' reserved property not allowed explicitly for an entity for entity id %s' %(nodeid)
                return error_helper(msg, 400)

        allPropnamesValid, prop = validate.checkAllPropnamesValid(en['properties'])
        if not allPropnamesValid:
            msg = str(prop)+' cannot begin or end with underscore for entity id %s' %(nodeid)
            return error_helper(msg, 400)

        ## MAJOR todo: determine automatically that the type is a list!!
        ## Also push it then like a list - but will have to maintain a list of props that can be list
        ## OR MV and check here back!

        nodelabels = en['labels']

        fetchdate = en['fetchdate']
        sourceurl = en['sourceurl']

        if not fetchdate.isdigit():
            msg = 'fecthdate should be a long time since epoch, negative if dates before 1970 for entity id %s' %(nodeid)
            return error_helper(msg, 400)

        if not validate.validateUrl(sourceurl):
            msg = 'sourceurl should be valid url for entity for entity id %s' %(nodeid)
            return error_helper(msg, 400)

        boolval, prop = validate.checkInternalProps(en['properties'])
        if not boolval:
            msg = 'prop %s not in correct format for entity id %s' %(prop,nodeid)
            return error_helper(msg, 400)

        nodeprops = {}
        for prop in en['properties']:

            # if prop != 'aliases': ##ALIASES CODE


            ##for all MV -- json.loads? or somehting else?
            nodeprops[prop] = en['properties'][prop]

        ### ALIASES CODE
        # nodeprops['aliases'] = []
        # for val in en['properties']['aliases']:
        #     nodeprops['aliases'].append(val)

        # nodeprops = en['properties']
        nodeprops['_pushdate_'] = getTimeNow()
        nodeprops['_crawl_en_id_'] = 'en_'+taskid+'_'+str(nodeid)
        # nodeprops['_token_'] = tokenid ##TODO: if you change this!, will have to change code for entity_read macro.
        nodeprops['_taskid_'] = taskid
        nodeprops['_nodenumber_'] = nodeid
        nodeprops['_pushedby_'] = userid
        nodeprops['_fetchdate_'] = int(fetchdate)
        nodeprops['_sourceurl_'] = sourceurl
        nodes[nodeid] = {'labels':nodelabels,'properties':nodeprops}


    required_reldict_props = ['label','properties','start_entity','end_entity','bidirectional','id','fetchdate','sourceurl']
    reserved_rel_props = ['crawl_rel_id','resolvedWithRELID','taskname','token','_token','workname','date','time','resolvedDate','resolvedAgainst','verifiedBy','resolvedBy','verifiedDate','update','lastUpdatedBy','lastUpdatedOn','_crawl_rel_id_','_token_','_taskname_','_id_','_relnumber_','taskid','_taskid_','verifiedby','_verifiedby_','verifydate',
    'pushdate','uuid','_uuid_','labels','_labels_'] ##just like the above _nodenumber_
    required_rel_props = [] ##inside entity['properties']

    for rel in relations:

        if not 'id' in rel:
            return error_helper('id required attribute missing for a relation', 400)

        linkid = rel['id']

        for prop in required_reldict_props:
            if not prop in rel:
                msg = str(prop)+' required attribute missing for relation id %s' %(linkid)
                return error_helper(str(prop)+' required attribute missing for a relation', 400)


        if linkid in links:
            msg = 'id repeated under relations for relation id %s' %(linkid)
            return error_helper(msg, 400)

        if not linkid.isdigit():
            msg = 'linkid is not a number for relation id %s' %(linkid)
            return error_helper(msg,400)

        linklabel = rel['label']

        if len(linklabel)<3:
            msg = 'Label too short for a relation for relation id %s' %(linkid)
            return error_helper(msg, 400)

        bidirectional = rel['bidirectional']

        if bidirectional!='True' and bidirectional!='False': ##decision taken avoid confusion yes no is default! ##TODO: add rules apis!
            msg = 'bidirectional not True/False for a for a relation for relation id %s' %(linkid)
            return error_helper(msg, 400)

        for prop in required_rel_props:
            if not prop in rel['properties']:
                msg = str(prop)+' required property missing for a relation for relation id %s' %(linkid)
                return error_helper(msg, 400)

        for prop in reserved_rel_props:
            if prop in rel['properties']:
                msg = str(prop)+' reserved property not allowed explicitly for a relation for relation id %s' %(linkid)
                return error_helper(msg, 400)

        allPropnamesValid, prop = validate.checkAllPropnamesValid(rel['properties'])
        if not allPropnamesValid:
            msg = str(prop)+' cannot begin or end with underscore for relation id %s' %(linkid)
            return error_helper(msg, 400)

        linkprops = rel['properties']
        fetchdate = rel['fetchdate']
        sourceurl = rel['sourceurl']

        if not fetchdate.isdigit():
            msg = 'fetchdate should be a long time since epoch, negative if dates before 1970 for relation id %s' %(linkid)
            return error_helper(msg, 400)

        if not validate.validateUrl(sourceurl):
            msg = 'sourceurl should be valid url for entity for relation id %s' %(linkid)
            return error_helper(msg, 400)

        boolval, prop = validate.checkInternalProps(linkprops)
        if not boolval:
            msg = 'prop %s not in correct format for relation id %s' %(prop, linkid)
            return error_helper(msg, 400)

        startnode = 'en_'+taskid+'_'+str(rel['start_entity'])
        endnode = 'en_'+taskid+'_'+str(rel['end_entity'])
        linkprops['_crawl_rel_id_'] = 'rel_'+taskid+'_'+str(linkid)
        #linkprops['_token_'] = tokenid
        linkprops['_taskid_'] = taskid
        linkprops['_relnumber_'] = linkid
        linkprops['bidirectional'] = bidirectional
        linkprops['_pushedby_'] = userid
        linkprops['_pushdate_'] = getTimeNow()
        linkprops['_fetchdate_'] = fetchdate
        linkprops['_sourceurl_'] = sourceurl


        links[linkid] = {'label':linklabel,'properties':linkprops,'start_entity':startnode, 'end_entity':endnode}


    posted, msg = postSubGraph(getGraph(), nodes, links, tokenid, taskid)

    if not posted:
        return error_helper(msg, 400)

    subgraph['entities'] = nodes
    subgraph['relations'] = links


    data = jsonify(subgraph)

    return data, 201 ## 201 is for creation!
    ##Usage: curl -i -H "Content-Type: application/json" -X POST -d '{"taskname":"wow","description":"Some values!"}' http://localhost:5000/newlinks/pushlinked/?_token=NexusToken2
