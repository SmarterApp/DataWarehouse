define [
  'jquery'
  'mustache'
  'edwareUtil'
  'edwareClientStorage'
  'text!edwareStickyCompareTemplate'
  'edwareGrid'
  'edwareEvents'
  'edwarePreferences'
], ($, Mustache, edwareUtil, edwareClientStorage, edwareStickyCompareTemplate, edwareGrid, edwareEvents, edwarePreferences) ->

  STICKY_POPOVER_TEMPLATE = '<div class="popover stickyPopover"><div class="mask"></div><div class="arrow"></div><div class="popover-inner large"><div class="popover-content"><p></p></div></div></div>'

  class EdwareGridStickyCompare

    constructor: (@labels, @callback) ->
      this.initialize()
      this

    initialize: () ->
      this.storage = edwareClientStorage.stickyCompStorage
      this.bindEvents()
      this.createButtonBar()
      this.selectedRows = {}
      this.compareSelectedActions = $('#compareSelectedActions')
      this.compareEnabledActions = $('#compareEnabledActions')
      this.stickyEnabledDescription = $('#stickyEnabledDescription')
      this.stickyCompareBtn = $('#stickyCompare-btn')
      this.stickyChainBtn = $('#stickyChain-btn')
      this.stickyChainText = $('#stickyChain-text')
      this.stickyClearLink = $('#stickyClear-lnk')
      this.stickyShowAllBtn = $('#stickyShowAll-btn')
      this.stickyInstTextPrefix = $('#stickyInstTextPrefix')

    # Sets information when we know what type of report it is, etc.
    # compareMode is set to false since we know that the html is reloaded
    setReportInfo: (@reportType, @displayType, @params) ->
      this.compareMode = false
      this.displayType = this.displayType.toLowerCase()

    update: () ->
      # Hide buttons based on whether any selection is already made
      # Only perform when compare mode is active
      if this.compareMode
        if this.getUniqueRowsCount() > 0
          this.showCompareEnabledButtons()
        else
          this.hideCompareSection()
      else
        # We may reach to this state when user selects some checkbox, and then submit a filter that cause grid to re-render
        if this.getUniqueRowsCount() is 0
          this.hideCompareSection()
        else
          # This happens when grid re-renders and we need to reapply selected rows with checkboxes to true and update its text
          this.applyCheckboxValues()

    applyCheckboxValues: () ->
      for rowId, data of this.selectedRows
        className = '.sticky_'+ rowId
        els = $(className)
        els.attr('checked', true)
        $(className + '.frozen-bdiv').attr('checked', true)
        this.checkedEvent els

    # All events related to grid filtering of rows
    bindEvents: () ->
      self = this
      # checkboxes in each row
      $(document).on 'click', '.stickyCheckbox', () ->
        if not $(this).is(':checked')
          self.removeCurrentRow this
          self.removeRowsForStudent this
          self.uncheckedEvent this
        else
          self.addCurrentRow this
          self.addRowsForStudent this
          self.checkedEvent this
        self.renderStickyChainRows()

      # Binds to compare button in summary row
      $(document).on 'click', '#stickyCompare-btn', () ->
        self.compare()

      # Text that appears next to checkbox after checkbox is clicked
      $(document).onClickAndEnterKey '.stickyCompareLabelChecked', () ->
        self.compare()

      # Deselect Button in summary row
      $(document).on 'click', '#stickyClear-lnk', () ->
        self.clearSelectedRows()
        $('.stickyCheckbox').attr('checked', false)
        # Remove class of checkedlabel, add class of regular label and then set the text
        label = $('.stickyCheckbox').siblings("label")
        label.toggleClass("stickyCompareLabel stickyCompareLabelChecked")
        label.text(self.labels.select)
        self.resetCompareRowControls()

      # Show all district button
      $(document).on 'click', '#stickyShowAll-btn', () ->
        # temporary save the selected rows to allow all the rows to appear in the grid
        selectedRows = self.selectedRows
        self.clearSelectedRows()
        self.updateSelection()
        self.selectedRows = selectedRows
        # Reapply checkbox value to the selected rows and then build chain list
        self.applyCheckboxValues()
        self.renderStickyChainRows()

      # Remove button on each row in grid
      $(document).onClickAndEnterKey '.stickyCompareRemove', () ->
        self.removeCurrentRow this
        self.updateSelection()

      # Remove Label
      $(document).on 'click', '.stickyRemoveLabel', () ->
        row = $(this).siblings('.stickyCompareRemove')
        self.removeCurrentRow row
        self.updateSelection()

      # remove icon on sticky chain
      $(document).on 'click', '.removeStickyChainIcon', () ->
        rowId = $(this).data('id')
        # Uncheck the checkbox in the grid
        elements = $('.sticky_' + rowId)
        elements.attr('checked', false)
        # We need to explicitly remove the rows
        # because we may run into the case where the row isn't loaded in the grid
        self.removeRowFromSelectedRows rowId
        self.uncheckedEvent elements
        $('.stickyChainScrollable').html(self.getStickyChainContent().html())

      # On logout, clear storage
      $(document).on 'click', '#logout_button', () ->
        # clear session storage
        self.storage.clear()

      $(document).on 'click', '.dropdown-menu .stickyChainScrollable', (e)->
        # To prevent the dropdown from closing when clicking inside dropdown menu
        e.stopPropagation()

    clearSelectedRows: () ->
      this.selectedRows = {}

    # Keep dates taken
    getUniqueRows: () ->
      keys = []
      for key, data of this.selectedRows
        item = {}
        item[key] =
          name : data.name
          asmts : data.asmts
        keys.push(item)
      keys

    getUniqueRowsCount: () ->
      @getUniqueRows().length

    # rows have been selected, compare the selections
    compare: () ->
      this.compareMode = true
      this.updateSelection() if this.getUniqueRowsCount() > 0

    # uncheck of checkbox event
    uncheckedEvent: (element) ->
      label = $(element).siblings("label")
      label.removeAttr('tabindex').text(this.labels.select)
      label.toggleClass("stickyCompareLabel stickyCompareLabelChecked")

      this.resetCompareRowControls()

    # checkbox has been checked
    checkedEvent: (element) ->
      $(element).siblings("label").toggleClass("stickyCompareLabelChecked stickyCompareLabel")
      this.resetCompareRowControls()

    # Given a row in the grid, add its value to selectedRows
    # for multi row student case, add dates
    addCurrentRow: (row) ->
      info = this.getCurrentRowInfo row
      viewName = edwarePreferences.getAsmtView()
      if !this.selectedRows[info.id]
        this.selectedRows[info.id] =
          name: info.name
      # Different asmts can be taken on the same date
      this.selectedRows[info.id].asmts ?= {}
      this.selectedRows[info.id].asmts[info.date] = viewName

    # Add other rows to selectedRows
    addRowsForStudent: (row) ->
      info = this.getCurrentRowInfo row
      viewName = edwarePreferences.getAsmtView()
      studentRowEls = elements = $('.sticky_' + info.id)
      # Add to selected rows
      for row in studentRowEls
        if !this.selectedRows[info.id].asmts[$(row).data('date')]
          this.addCurrentRow row
      # Check all rows on
      this.applyCheckboxValues()

    # Given a row in the grid, remove its value from selectedRows
    removeCurrentRow: (row) ->
      info = this.getCurrentRowInfo row
      this.removeRowFromSelectedRows info.id

    removeRowsForStudent: (row) ->
      className = $(row).data('value')
      $('#gbox_gridTable .sticky_' + className).attr('checked', false)

    removeRowFromSelectedRows: (id) ->
      delete this.selectedRows[id]

    # Returns the id and name of a row
    getCurrentRowInfo: (row) ->
      {'id': $(row).data('value'), 'name': $(row).data('name'), 'date': $(row).data('date')}

    getSelectedRowsFromStorage: () ->
      # When this gets called, it means we should read from storage
      # Set the mode based on whether any rows are returned
      # Gets the rows selected for the current report view
      rows = this.getDataForReport()
      this.selectedRows = {}
      viewName = edwarePreferences.getAsmtView()
      for row in rows
        for key, data of row
          this.selectedRows[key] =
            name: ''
          this.selectedRows[key].asmts ?= data.asmts
          # this.selectedRows[key].asmts[date] ?= viewName
      this.compareMode = rows.length > 0
      this.getUniqueRows()

    getFilteredInfo: (allData, columnField) ->
      # client passes in data and this will return rows that user have selected and whether stickyCompare is enabled
      # We need the columnField that corresponds to each data row to build sticky chain list
      returnData = []
      # show all records
      selectedRows = @getSelectedRowsFromStorage()
      viewName = edwarePreferences.getAsmtView()
      if selectedRows.length is 0
        return {'data': allData, 'enabled': false }
      for item in allData
        for row in selectedRows
          for key, data of row
            # Display per date per view
            if String(item.rowId) is key
             # and data.asmts[item.dateTaken]
              returnData.push item
              # Repopulate the names of the rows for sticky chain in the case of user clicking on "show all"
              @selectedRows[key] =
                name: item[columnField]
                asmts: data.asmts
      return {'data': returnData, 'enabled': selectedRows.length > 0}


    reset: () ->
      this.selectedRows = {}
      this.compareMode = false
      this.saveSelectedRowsToStorage()

    getDataForReport: () ->
      # Gets the rows selected for the current report view
      data = this.getDataFromStorage()[this.reportType] || {}
      data[this.getKey()] || []

    # Saves to storage
    # Reset compare mode depending on whether any rows are selected
    updateSelection: () ->
      this.saveSelectedRowsToStorage()
      if this.getUniqueRowsCount() is 0 and this.compareMode
        this.compareMode = false
        this.hideCompareSection()
      # calls a callback function (render grid)
      this.callback()

    # Update session storage for selected rows
    saveSelectedRowsToStorage: () ->
      data = this.getDataFromStorage()
      reportData = data[this.reportType]
      reportData = {} if not reportData
      reportData[this.getKey()] = this.getUniqueRows()
      data[this.reportType] = reportData
      this.storage.save data

    getDataFromStorage: () ->
      data = JSON.parse(this.storage.load())
      if not data then data = {}
      data

    getKey: () ->
      if this.params['schoolId'] and this.params['asmtGrade']
        # cache key for los is a combination of schoolguid and asmtGrade
        id = this.params['schoolId'] + "_" + this.params['asmtGrade']
      else if this.params['districtId']
        id  = this.params['districtId']
      else if this.params['stateCode']
        id  = this.params['stateCode']
      id

    getDisplayTypes: () ->
      # Returns the plural form of displayType
      this.displayType + "s"

    # Reset Grid rows checkbox and button text
    resetCompareRowControls: () ->
      text = this.labels.filter
      labelNameKey = this.displayType
      count = this.getUniqueRowsCount()
      if count > 0
        labelNameKey = this.getDisplayTypes() if count > 1
        countText = count + " " + this.labels[labelNameKey]
        this.showCompareSelectedButtons()
      else
        # Hide all buttons
        this.hideCompareSection()
      text += " " + countText if countText
      $('.stickyCheckbox:checked').siblings("label")\
        .attr('tabindex', '0').text(text)
      # To display ex. "districts_selected" label
      instText = this.labels["sticky_inst_text"]
      output = Mustache.to_html instText[labelNameKey], {'filterNumber': count}
      this.stickyInstTextPrefix.html(output)
      this.stickyChainText.text("#{count} #{this.labels[labelNameKey + "_selected"]}")

    createButtonBar: () ->
      output = Mustache.to_html edwareStickyCompareTemplate, {'labels': this.labels}
      $('#stickyCompareSection').html output
      this.compareSection = $('#stickyCompareSection')
      this.hideCompareSection()

    hideCompareSection: () ->
      if @stickyChainBtn isnt undefined and @stickyChainBtn.parent().find(".popover").length isnt 0
        @stickyChainBtn.popover "hide"
        @stickyChainBtn.parent().removeClass "open"
      this.compareSection.hide()
      edwareGrid.adjustHeight()

    showCompareSection: () ->
      this.compareSection.show()
      edwareGrid.adjustHeight()

    showCompareSelectedButtons: () ->
      this.showCompareSection()
      this.compareSelectedActions.show()
      this.compareEnabledActions.hide()

    showCompareEnabledButtons: () ->
      this.showCompareSection()
      this.stickyShowAllBtn.text(this.labels.show_all + " " + this.labels[this.getDisplayTypes()])
      count = this.getUniqueRowsCount()
      text = this.labels.viewing + " " + String(count) + " "
      if count > 1 then text += this.labels[this.getDisplayTypes()] else text += this.labels[this.displayType]
      this.stickyEnabledDescription.text(text)
      this.compareSelectedActions.hide()
      this.compareEnabledActions.show()

    getStickyChainContent: ()->
      reverse = {}
      names = []
      for key, data of this.selectedRows
        reverse[data.name] = key
        names.push data.name
      names = names.sort()
      idx = 0
      scrollable =$('<div class="stickyChainScrollable"></div>')
      table = $('<div class=" stickyChainTable"></div>')
      for name in names
        table.append $('<div class="tableRow"><hr class="tableCellHR"/><hr class="tableCellHR"/></div>') if idx > 0
        table.append $("<div class='tableRow'><div class='tableCellLeft'>#{name}</div><a aria-label='click to remove #{name}' href='#' data-id='#{reverse[name]}' class='tableCellRight removeStickyChainIcon'></a></div>")
        idx++
      scrollable.append table

    renderStickyChainRows: () ->
      # TODO:
      self = this
      @stickyChainBtn.popover
        html: true
        placement: 'bottom'
        trigger: 'manual'
        template: STICKY_POPOVER_TEMPLATE
        content: -> $('<div></div>').append(self.getStickyChainContent()).html()
      .mouseover ->
        if $(this).parent().find('.popover').length is 0
          btnGroupElement = $(this).parent()
          btnGroupElement.addClass 'open'
          $(this).popover 'show'
          popoverElement = $(this).parent().find('.popover')
          popoverElement.css 'left', 0
          popoverElement.find('.arrow').css 'left', self.stickyChainBtn.width()/2
          btnGroupElement.mouseleave ->
            self.stickyChainBtn.popover 'hide'
            btnGroupElement.removeClass 'open'

          btnGroupElement.focuslost ()->
            # collpase on foucs out
            $(this).mouseleave()
      .focus ->
        $(this).mouseover()


  EdwareGridStickyCompare:EdwareGridStickyCompare
