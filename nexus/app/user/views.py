from app.user import user
from flask import render_template, flash, redirect, session, g, request, url_for, abort
from app.forms import EditEntityForm, form_error_helper

@user.route('/')
def show():
	from app.models.dbmodels.user import User
	user = User.getUser(session['userid'])
	return render_template("user_profile.html", user = user)


# # TODO: check if the ending forward slashes are there for all
# #  do it when checking
# @user.route('/editEntity/<int:uuid>/',methods=["GET","POST"])
# def editEntity(uuid):
# 	##fetch current details for now
# 	##show these current details
# 	##edit form of entity?
# 	##wait for moderation
#
# 	##for now lets just show the current text
# 	##and give a text area for updating the text
# 	##let the user update it
# 	##we will save both in a db
# 	##who to any moderator who logs in afterwards
# 	##who approves dispapproves --> and the change goes to the db
# 	##will save this to a log
#
# 	##TODO: UUIDS are not changeable for ever, make a check of that
#
#
# 	# delete a node with uuid and create a node
#
# 	from app.graphdb import *
# 	node = entity(uuid)
# 	entity = str(node)
#
# 	form = EditEntityForm()
# 	if form.validate_on_submit():
# 		try:
# 			newnodetext = form.new_entity.data
# 			newnodetext = newnodetext.strip()
# 			nayanode = deserializeNode(newnodetext)
# 			updatePrev(uuid,nayanode)
# 			flash(newnodetext)
# 			return redirect('entity/'+str(uuid))
# 		except Exception as e:
# 			print 'Exception'
# 			print e
# 			flash('Form not filled properly')
# 	else:
# 		form_error_helper(form)
# 	return render_template("edit_entity.html", homeclass="active",uuid=str(uuid), entity=entity, form=form)


##TODO: check if the ending forward slashes are there for all
## do it when checking
@user.route('/temp/')
def temp():
	##fetch current details for now
	##show these current details
	##edit form of entity
	##wait for moderation
	return render_template("temp.html", temptext='temp')

@user.route('/edit/<string:kind>/<int:objid>/', methods=["GET","POST"])
def edit(kind, objid):

	##even if you delete aliases and add only one value, it will take is a listld be no issue
	##comma seperated
	# livedin mvp, a prop will come for our mvp, assume something ##alsg se tab
	#
	# livedin a mvp prop will change to relation
	# bornin a prop will change to relation
	# diedin a prop will change to relation
	# aliases, livedin
	##also countries related to

	from app.models.graphmodels.graph_handle import GraphHandle
	gg = GraphHandle()

	labels  = []

	obj = gg.getOriginalCoreObject(kind, objid)
	copyobj = gg.coredb.copyObjectAsItIs(kind, obj)

	labels = diffLabelsNeeded(kind)

	needed = diffPropsNeeded(copyobj,kind=kind)
	##helps!!
	for prop in needed:
		copyobj[prop] = ''

	if request.form:
		sourceurl = request.form.get('sourceurl')

		print sourceurl
		print len(sourceurl)
		flash(sourceurl)

		propnames = request.form.getlist('propname[]')
		propvals = request.form.getlist('propval[]')

		orignames = request.form.getlist('actualpropname[]')
		origvals = request.form.getlist('actualpropval[]')

		##will be empty if relation
		origlabels = request.form.getlist('origlabel[]')
		newlabels = request.form.getlist('newlabel[]')



		newobj = gg.coredb.copyObjectAsItIs(kind, copyobj)

		# ignore uuid
		# if props with same name again , consider later one
		# if
		flash(str(propnames)+ " ::::: " +str(propvals))
		newpropdict = {}
		ll = len(propnames)
		for i in range(ll):
			if (len(propnames[i].strip())>1):
				if (len(propvals[i].strip())>0):
					newpropdict[propnames[i]] = propvals[i]

		flash(str(orignames) + " :::::: " +str(origvals))
		#flash(str(needednames) +" :::::: "+str(neededvals))
		flash(str(newlabels))

		newlabelsnonempty = []
		for label in newlabels:
			if len(label.strip())>0:
				newlabelsnonempty.append(label.strip())

		newobj = gg.coredb.copyObjectAsItIs(kind, copyobj)

		ll = len(origvals)
		origpropdict = {}
		for i in range(ll):
			if (len(orignames[i].strip())>1):
				if (len(origvals[i].strip())>0):
					newobj[orignames[i].strip()] = origvals[i].strip()


		flag = False
		msg = ""

		if sourceurl is None or len(sourceurl)<10:
			msg = msg + 'sourceurl check again' +';;;'
			flag = True

		for prop in newpropdict:
			if prop in newobj:
				msg = msg + ' Added a custom prop that has same name as in our required prop list' +';;;'
				flag = True

		if flag:
			flash(msg)
			return render_template('user_edit.html', sourceurl =sourceurl,  obj = newobj, newpropdict=newpropdict, needed = needed, labels=labels, newlabels=newlabelsnonempty, kind=kind, objid=objid)

		else:

			nayaobj = gg.coredb.copyObjectAsItIs(kind, newobj)

			for label in newlabelsnonempty:
				nayaobj.labels.add(label)

			for prop in newpropdict:
				nayaobj[prop] = newpropdict[prop]

			for prop in newobj.properties:
				if len(str(newobj[prop]).strip())==0:
					nayaobj[prop]=None

			##adding MVP patch for wiki:
			from app.constants import MVPLIST
			for prop in MVPLIST:
				if prop in nayaobj:
					nayaobj[prop] = nayaobj[prop].split(',')

			###XXX:
			##make a json TODO
			##validate json api call normal without token
			##whould give true
			#json object to be made at this point for this object remove uuid and stuff
			###and then validate that json using the code in api, when merge! TODO

			ID_NAME = gg.getCoreIDName(kind)
			curr_id = nayaobj[ID_NAME]
			nayaobj[ID_NAME] = None

			someobj = gg.wikiObjCreate(kind, curr_id,  nayaobj, session['userid'], sourceurl)

			flash(str(someobj))

			flash('Successfully pushed for moderation')

			if kind=='node':
				return redirect(url_for('readEntity',uuid=objid))
			if kind =='relation':
				return redirect(url_for('readRelation',relid=objid))


	return render_template('user_edit.html', sourceurl='', obj  = copyobj, needed = needed,  labels=labels, kind=kind, objid=objid)


@user.route('/history/<int:uuid>/<string:prop>/')
def history(uuid,prop):
	return render_template("temp.html", temptext=str(uuid)+' and prop '+prop)

def diffLabelsNeeded(kind):


	mains = ['person','list','organization']
	subperson = ['businessPerson','politician','mediaPerson','lawPerson','primeMinister','chiefMinister','governor','memberOfParliament']
	suborg = ['school','business','privateCompany','publicCompany','mediaOrganization','notForProfit','government','socialClub']
	networks = ['indian','foreign']
	nodelabels =  mains+subperson+suborg+networks


	rellabels = ['worksIn','memberOf','family','spouseof']

	if kind == 'node':
		return nodelabels
	else:
		return rellabels

def diffPropsNeeded(node, kind='node'):

		# for person
		# not for organization
		# not for list
		ans = []

		if kind== 'node':
			props1 = ['name','blurlb','bio','startdate','enddate','iscurrent','website']

			##if person
			props2 = []
			if 'person' in node.labels:
				props2 = ['firstname','lastname','middlename','namesuffix','nameprefix'] ##idea of legal name from fn, ln mn


			props3 = ['startplace', 'endplace']

			props = props1 +props2 +props3 ##all these are person props


			for prop in props:
				if prop not in node.properties:
					ans.append(prop)


		else:

			props = ['startdate','enddate','iscurrent']
			for prop in props:
				if prop not in node.properties:
					ans.append(prop)




		return ans
