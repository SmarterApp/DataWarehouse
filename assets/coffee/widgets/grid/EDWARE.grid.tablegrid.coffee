define [
  'jquery'
  'jqGrid'
  'edwareUtil'
  'edwareGridFormatters'
], ($, jqGrid, edwareUtil, edwareGridFormatters) ->

  DEFAULT_CONFIG =
    tableId: 'gridTable'
    data: undefined
    options:
      gridHeight: window.innerHeight * 0.6 #default grid height
      datatype: "local"
      height: "auto"
      viewrecords: true
      autoencode: true
      rowNum: 100
      gridview: true
      scroll: 1
      shrinkToFit: false
      defaultWidth: 980
      loadComplete: () ->


  class EdwareGrid

    constructor: (@table, columns, @options, @footer) ->
      this.columns = this.setSortedColumn columns
      this.options.footerrow = true if this.footer
      self = this
      this.options.loadComplete = () ->
        self.afterLoadComplete()

    setSortedColumn: (columns) ->
      sorted = this.options.sort
      return columns if not sorted

      for column in columns
        for item in column['items']
          if sorted.name == item.index
            item.sortorder = sorted.order || 'asc'
        column

    afterLoadComplete: () ->
      # Move footer row to the top of the table
      $("div.ui-jqgrid-sdiv").insertBefore $("div.ui-jqgrid-bdiv")
      $("#gview_gridTable > .ui-jqgrid-bdiv").css {
          'min-height': 100, 'height': this.options.gridHeight
      }
      this.highlightSortLabels()
   
    render: ()->
      this.renderBody()
      this.renderHeader()
      this.renderFooter()

    renderBody: () ->
      colNames = this.getColumnNames()
      colModel = this.getColumnModels()
      options = $.extend(this.options,
        colNames: colNames
        colModel: colModel
        # This sets the sort arrows to be shown on sortable columns
        viewsortcols: [true, 'vertical', true]
      )
      this.table.jqGrid options
      this.table.jqGrid "hideCol", "rn"
      this.table.setGridWidth options.defaultWidth, false

    renderFooter: () ->
      # Add footer row to the grid
      footer = this.footer
      this.table.jqGrid('footerData','set', footer, true) if footer

    renderHeader: () ->
      headers = this.getHeaders()
      return if headers.length <= 0
      # draw headers
      this.table.jqGrid "setGroupHeaders", {
        useColSpanStyle: false
        groupHeaders: headers
        fixed: true
      }

    getColumnNames: () ->
      columnNames = []
      for column in this.columns
        for item in column['items']
          columnNames.push this.getColumnName(item)
      columnNames

    getColumnModels: () ->
      models = []
      for column in this.columns
        for item in column['items']
          item.parent = column
          models.push this.getColumnModel item
      models

    getColumnModel: (column) ->
      colModelItem =
        name: column.field
        label: column.name
        parentLabel: column.parent.name
        index: column.index
        width: column.width
        resizable: false # prevent the user from manually resizing the columns

      colModelItem.formatter = (edwareGridFormatters[column.formatter] || column.formatter) if column.formatter
      colModelItem.formatoptions = column.options if column.options
      colModelItem.sorttype = column.sorttype if column.sorttype
      colModelItem.sortable = column.sortable
      colModelItem.align = column.align if column.align
      colModelItem.labels = this.options.labels
      colModelItem.title = column.title
      colModelItem.classes = column.style if column.style
      colModelItem.frozen = column.frozen if column.frozen
      colModelItem.export = column.export
      colModelItem.stickyCompareEnabled = this.options.stickyCompareEnabled

      #Hide column if the value is true
      if column.hide
        colModelItem.cellattr = (rowId, val, rawObject, cm, rdata) ->
          ' style="display:none;"'
      this.options.sortorder = column.sortorder  if column.sortorder
      this.options.sortname = column.index  if column.sortorder
      colModelItem

    getColumnName: (column) ->
      column.name + column.displayTpl

    getHeaders: () ->
      for column in this.columns
        startColumnName: column.items[0].field
        numberOfColumns: column.items.length
        titleText: column.name

    highlightSortLabels: () ->
      $('.jqg-third-row-header .ui-th-ltr').removeClass('active')
      grid = $('#gridTable')
      column = grid.jqGrid('getGridParam', 'sortname')
      grid.jqGrid('setLabel', column, '', 'active')

    $.fn.edwareGrid = (columns, options, footer) ->
      this.grid = new EdwareGrid(this, columns, options, footer)
      this.grid.render()
      
      # trigger gridComplete event
      options.gridComplete() if options.gridComplete

    $.fn.eagerLoad = () ->
      # load all data at once
      this.jqGrid('setGridParam', {scroll: false, rowNum: 100000}).trigger("reloadGrid")

    $.fn.lazyLoad = () ->
      # dynamically load data when scrolling down
      this.jqGrid('setGridParam', {scroll: 1, rowNum: 100}).trigger("reloadGrid")

  #
  #    * Creates EDWARE grid
  #    * @param tableId - The container id for grid
  #    * @param columnItems
  #    * @param columnData
  #    * @param footerData - Grid footer row
  #    * @param options
  #
  create = (config) ->
    # merge configuration
    config = $.extend true, {}, DEFAULT_CONFIG, config
    options = config['options']
    data = config['data']
    options.data = data
    columns = config['columns']
    footer = config['footer']
    if data and data[0]
      edwareUtil.displayErrorMessage ''
      $('#' + config['tableId']).edwareGrid columns, options, footer
    else
      edwareUtil.displayErrorMessage  options.labels['no_results']

  create: create

