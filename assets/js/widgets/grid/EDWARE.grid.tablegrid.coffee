define [
  'jquery'
  'jqGrid'
  'cs!EDWARE'
  'cs!edwareUtil'
  'cs!edwareGridFormatters'
], ($, jqGrid, EDWARE, edwareUtil, edwareGridFormatters) ->
  #
  # * EDWARE grid
  # * The module contains EDWARE grid plugin and grid creation method
  # 
    
    #
    #    *  EDWARE Grid plugin
    #    *  @param panelConfig - Panel config data
    #    *  @param options
    #    *  Example: $("#table1").edwareGrid(columnItems, gridOptions)
    #    
    
    (($) ->
      $.fn.edwareGrid = (panelConfig, options) ->
        colNames = []
        colModel = []
        groupHeaders = []
        if panelConfig
          i = 0
          while i < panelConfig.length
            item = panelConfig[i]
            if item.items and item.items.length > 0
              items = item.items
              groupHeaders.push
                startColumnName: item.items[0].field
                numberOfColumns: item.items.length
                titleText: item.name
            
            else
              items = [item]
              
            j = 0
            while j < items.length
              
              item1 = items[j]
              colNames.push item1.name
              colModelItem =
                name: item1.field
                index: item1.field
                width: item1.width
  
              colModelItem.formatter = (if (edwareGridFormatters[item1.formatter]) then edwareGridFormatters[item1.formatter] else item1.formatter)  if item1.formatter
              colModelItem.formatoptions = item1.params  if item1.params
              colModelItem.sorttype = item1.sorttype  if item1.sorttype
              colModelItem.align = item1.align  if item1.align
              colModelItem.classes = item1.style  if item1.style
              options.sortorder = item1.sortorder  if item1.sortorder
              options.sortname = item1.field  if item1.sortorder
              colModelItem.resizable = false # prevent the user from manually resizing the columns
              colModel.push colModelItem
              j++
              
            i++
          options = $.extend(options,
            colNames: colNames
            colModel: colModel
            onSortCol: (index, idxcol, sortorder) ->
          
              # show the icons of last sorted column
              $(@grid.headers[@p.lastsort].el).find(">div.ui-jqgrid-sortable>span.s-ico").show()  if @p.lastsort >= 0 and @p.lastsort isnt idxcol and @p.colModel[@p.lastsort].sortable isnt false
          )
        $(this).jqGrid options
        $(this).jqGrid "hideCol", "rn"
        

        
        colModel = $(this).jqGrid("getGridParam", "colModel")
        $("#gbox_" + $.jgrid.jqID($(this)[0].id) + " tr.ui-jqgrid-labels th.ui-th-column").each (i) ->
          cmi = colModel[i]
          colName = cmi.name
          if cmi.sortable isnt false
            
            # show the sorting icons
            $(this).find(">div.ui-jqgrid-sortable>span.s-ico").show()
          
          # change the mouse cursor on the columns which are non-sortable
          else $(this).find(">div.ui-jqgrid-sortable").css cursor: "default"  if not cmi.sortable and colName isnt "rn" and colName isnt "cb" and colName isnt "subgrid"


        if groupHeaders.length > 0
          $(this).jqGrid "setGroupHeaders",
            useColSpanStyle: false
            groupHeaders: groupHeaders
            fixed: true
            
        $(this).find(".jqg-second-row-header th:first-child").css "background", "#ffffff"
        
    ) jQuery
    
    #
    #    * Creates EDWARE grid
    #    * @param tableId - The container id for grid
    #    * @param columnItems
    #    * @param columnData
    #    * @param assessmentCutpoints
    #    * @param options
    #    
    create = (tableId, columnItems, columnData, options) ->
      
      columnData = columnData[columnItems.root]  if columnItems.root and columnData isnt null and columnData isnt `undefined`
      
      gridOptions =
        data: columnData
        datatype: "local"
        height: "auto"
        viewrecords: true
        autoencode: true
        rowNum: 10000
        loadComplete: ->
           $("tr.jqgrow:odd").css "background", "#f8f8f8"
  
      if columnData is null or columnData is `undefined` or columnData.length < 1
        edwareUtil.displayErrorMessage "There is no data available for your request. Please contact your IT administrator."
      else
        gridOptions = $.extend(gridOptions, options)  if options
        $("#" + tableId).edwareGrid columnItems, gridOptions
        
    create: create