odoo.define('bi_mass_duplicate.ListExtend', function (require) {
"use strict";
var core = require('web.core');
var BasicController = require('web.BasicController');
var DataExport = require('web.DataExport');
var Sidebar = require('web.Sidebar');
var session = require('web.session');
var _t = core._t;
var qweb = core.qweb;
var ListController = require('web.ListController');
var ListExtend = ListController.include({

	init: function (parent, model, renderer, params) {
		this._super.apply(this, arguments);
		this.hasSidebar = params.hasSidebar;
		this.toolbarActions = params.toolbarActions || {};
		this.editable = params.editable;
		this.noLeaf = params.noLeaf;
		this.selectedRecords = []; // there is no selected record by default
	},

	renderSidebar: function ($node) {
		var self = this;
		if (this.hasSidebar && !this.sidebar) {
			var other = [{
				label: _t("Export"),
				callback: this._onExportData.bind(this)
			}];
			if (this._onToggleArchiveState){
				if (this.archiveEnabled) {
					other.push({
						label: _t("Archive"),
						callback: this._onToggleArchiveState.bind(this, true)
					});
					other.push({
						label: _t("Unarchive"),
						callback: this._onToggleArchiveState.bind(this, false)
					});
				}
			}
			if (this._onDuplicateRecord){
				if (this.is_action_enabled('create') && this.is_action_enabled('duplicate')) {
					other.push({
						label: _t('Mass Duplicate'),
						callback: this._onDuplicateRecord.bind(this),
					});
				}
			}
			if (this._onDeleteSelectedRecords){
				if (this.is_action_enabled('delete')) {
					other.push({
						label: _t('Delete'),
						callback: this._onDeleteSelectedRecords.bind(this)
					});
				}
			}
			this.sidebar = new Sidebar(this, {
				// editable: this.is_action_enabled('edit'),
				env: {
					context: this.model.get(this.handle, {raw: true}).getContext(),
					activeIds: this.getSelectedIds(),
					model: this.modelName,
				},
				actions: _.extend(this.toolbarActions, {other: other}),
			});
			return this.sidebar.appendTo($node).then(function() {
                self._toggleSidebar();
            });
		}
		return Promise.resolve();
	},

	_onDuplicateRecord: function () {
		var self = this;
		this.duplicateRecord(this.selectedRecords,self.modelName)
			.then(function () {
				
			});
	},

	duplicateRecord: function (recordIds,modelname) {
		var self = this;
		var i = null;
		var lst=[];
		// var m =self.model;
		var res = [];
		// var record = this.model.localData[recordIds];
		var records = _.map(recordIds, function (id) { return self.model.localData[id]; });
		var context =this.model._getContext(records);;
		for(var x =0;x<records.length;x++)
		{
			lst.push(records[x]);
		}
		return this._rpc({
				model : 'mass.duplicate',
				method : 'mass_copy',
				args :[1,lst],
				context: context,
				}).then(function () {
					self.update({});
                });
	},

});


return ListExtend;

});