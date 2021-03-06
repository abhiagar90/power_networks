from app.mod import mod
from flask import render_template, flash, redirect, session, g, request, url_for, abort, jsonify

@mod.route('/')
def show():
    from app.models.dbmodels.user import User
    flash(str(User.validateToken('abhi10@gmail.com','2ee457b79dsd6f81eab77431876d57bac99')))

    from app.models.dbmodels.tasks import Taskusers
    flash(Taskusers.validateTaskAndUser(taskid=1,userid='abhi2@gmail.com'))

    from app.models.dbmodels.user import User
    usr = User.getUser(userid='abhi@gmail.com')
    ##check usr not None
    ##will be from session
    ## usr.apikey ## get this


    return render_template("mod_home.html")




##adding code here so that user work doesnt clutter
##but move this to user at the onset!
@mod.route('/trial/')
def trial():
    ##user gives certain data we have changed object let's say
    from app.models.graphmodels.graph_handle import GraphHandle
    from app.utils.commonutils import Utils
    from app.constants import CRAWL_TASKID, CRAWL_PUSHDATE, CRAWL_PUSHEDBY, CRAWL_TASKTYPE
    from app.constants import CRAWL_SOURCEURL, CRAWL_FETCHDATE, CRAWL_EN_ID_NAME, RESOLVEDWITHUUID
    from app.constants import CRAWL_NODENUMBER, CRAWL_EN_ID_FORMAT

    gg = GraphHandle()
    node = gg.getOriginalCoreObject('node',77)
    copynode = gg.coredb.copyNode(node)

    ##TODO: copy the labels that is imp
    ##get uuid that is imp
    ##do your changes as you get from the html form, then push them to crawldb
    ##with the changes that we have done here
    ##TODO:
    # think if you need to use the api push? we need to save the task id too! seems overkill.

    copynode['uuid'] = None ##remove for now
    copynode[RESOLVEDWITHUUID] = 77
    copynode[CRAWL_PUSHEDBY] = 'abhi10@gmail.com'
    copynode[CRAWL_PUSHDATE] = Utils.currentTimeStamp()
    #XXX: for user ownerid = session['userid'] and iscrawled = 0, get the unique row
    ##that's our taskid
    copynode[CRAWL_TASKID] = 3 ##get from db for thi user
    copynode[CRAWL_SOURCEURL] = "http://wikipedia.com/NaveenJindal/"
    copynode[CRAWL_FETCHDATE] = copynode[CRAWL_PUSHDATE]-4000000
    copynode[CRAWL_TASKTYPE] = "wiki"
    copynode['job'] = "just farmer"
    #copynode.labels.add('personOfTheYear')
    copynode[CRAWL_NODENUMBER] = int(Utils.currentTimeStamp()) ##though idiotic, we wont be needing it for this!
    ##but for generating a unique name na!

    copynode[CRAWL_EN_ID_NAME] = CRAWL_EN_ID_FORMAT %(copynode[CRAWL_TASKID], copynode[CRAWL_NODENUMBER])

    #flash(str(node))
    flash(copynode)

    gg.crawldb.graph.create(copynode)
    copycopynode = gg.getCrawlObjectByID('node',CRAWL_EN_ID_NAME,copynode[CRAWL_EN_ID_NAME],True)
    flash(copycopynode)


    ##TODO: same things for relations
    return render_template("temp.html", temptext='trial completed')

@mod.route('/trial2/')
def mod2():

    ##user gives certain data we have changed object let's say
    from app.models.graphmodels.graph_handle import GraphHandle
    from app.utils.commonutils import Utils

    from app.constants import CRAWL_TASKID, CRAWL_PUSHDATE, CRAWL_PUSHEDBY, CRAWL_TASKTYPE
    from app.constants import CRAWL_SOURCEURL, CRAWL_FETCHDATE, CRAWL_EN_ID_NAME, RESOLVEDWITHUUID, RESOLVEDWITHRELID
    from app.constants import CRAWL_NODENUMBER, CRAWL_EN_ID_FORMAT, CRAWL_RELNUMBER, CRAWL_REL_ID_NAME

    gg = GraphHandle()
    rel = gg.getOriginalCoreObject('relation', 21)
    copyrel = gg.coredb.copyRelation(rel)
    flash(rel)
    flash(copyrel)

    ##TODO: copy the labels that is imp
    ##get uuid that is imp
    ##do your changes as you get from the html form, then push them to crawldb
    ##with the changes that we have done here
    ##TODO:
    # think if you need to use the api push? we need to save the task id too! seems overkill.

    copyrel['relid'] = None ##remove for now
    copyrel[RESOLVEDWITHRELID] = 21
    copyrel[CRAWL_PUSHEDBY] = 'abhi10@gmail.com'
    copyrel[CRAWL_PUSHDATE] = Utils.currentTimeStamp()
    # #XXX: for user ownerid = session['userid'] and iscrawled = 0, get the unique row
    # ##that's our taskid
    copyrel[CRAWL_TASKID] = 3
    copyrel[CRAWL_SOURCEURL] = "http://wikipedia.com/NaveenJindal/"
    copyrel[CRAWL_FETCHDATE] = copynode[CRAWL_PUSHDATE]-4000000
    copyrel[CRAWL_TASKTYPE] = "wiki"
    copyrel['startdate'] = "30 March 2010"
    # #copynode.labels.add('personOfTheYear')

    copyrel[CRAWL_RELNUMBER] = 1 ##though idiotic
    copyrel[CRAWL_REL_ID_NAME] = CRAWL_EN_ID_FORMAT %(copynode[CRAWL_TASKID], copynode[CRAWL_NODENUMBER])


    # #flash(str(node))
    # flash(copynode)
    #
    # gg.crawldb.graph.create(copynode)
    # copycopynode = gg.getCrawlObjectByID('node',CRAWL_EN_ID_NAME,copynode[CRAWL_EN_ID_NAME],True)
    # flash(copycopynode)
    #
    #
    # ##TODO: same things for relations

    return render_template("temp.html", temptext='trial completed')




@mod.route('/relform/', methods=["GET","POST"])
def relform():


    if request.form:

        names = request.form.getlist('propname[]')
        actualnames = request.form.getlist('actualpropname[]')
        needednames = request.form.getlist('neededpropname[]')

        neededvals = request.form.getlist('neededpropval[]')
        actualvals = request.form.getlist('actualpropval[]')
        namevals = request.form.getlist('propval[]')



        # ignore uuid
        # if props with same name again , consider later one
        # if
        flash(str(names)+ " ::::: " +str(namevals))
        flash(str(actualnames) + " :::::: " +str(actualvals))
        flash(str(needednames) +" :::::: "+str(neededvals))
        # flash(str(labels))


    from app.models.graphmodels.graph_handle import GraphHandle
    gg = GraphHandle()
    node = gg.getOriginalCoreObject('relation', 1)
    copynode = gg.coredb.copyRelation(node)

    needed = diffPropsNeeded(copynode,kind='relation')

    # from app.utils.commonutils import Utils
    # #copynode['uuid'] = None ##remove for now

    # flash('Normal')
    return render_template('wiki_form.html', node  = copynode, needed = needed, kind='relation')

## follows the same structure as in verifier work
@mod.route('/pickobject/<string:kind>/')
def pickobject(kind):

    from app.models.graphmodels.graph_handle import GraphHandle
    from app.constants import CRAWL_EN_ID_NAME, RESOLVEDWITHUUID

    gg = GraphHandle()

    CRAWL_ID_NAME, CURR_ID = gg.getTwoVars(kind)

    session.pop(CRAWL_ID_NAME, None)
    session.pop(CURR_ID, None)
    session.pop('kind', None)

    nodecount = gg.crawldb.getResolvedButNotModeratedNodeCount()

    node = None
    if nodecount!=0:
        node = gg.nextNodeToModerate(session['userid'])
        print 'hereeeeeeeee'
    if node is None:
        ##TODO: pass redirect or something
        abort(404)
        pass

    session[CRAWL_ID_NAME] = node[CRAWL_EN_ID_NAME]

    session[CURR_ID] = node[RESOLVEDWITHUUID]
    session['kind'] = kind

    print 'sessionnnnnnnnnn'
    print session[CRAWL_ID_NAME],  session[CURR_ID],  session['kind']


    return redirect(url_for('verifier.diffPushGen', kind=kind))


@mod.route('/temp/<string:kind>/<int:uuid>/')
def temp(kind,uuid):
    ##uuid
    from app.models.graphmodels.graph_handle import GraphHandle
    gg = GraphHandle()
    obj = gg.getOriginalCoreObject(kind,uuid)
    msg = ''
    for prop in obj.properties:
        print '----------'
        print prop
        print type(obj[prop])
        print '----------'
        msg = msg + '(%s: %s) || ' %(prop, str(type(obj[prop])))

    return render_template('temp.html',temptext=msg)
