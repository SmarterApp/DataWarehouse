###
# Comparing Population Report #

###

define [
  "jquery"
  "bootstrap"
  "mustache"
  "edwareDataProxy"
  "edwareGrid"
  "edwareBreadcrumbs"
  "edwareUtil"
  "edwareFooter"
  "edwareHeader"
  "edwareDropdown"
], ($, bootstrap, Mustache, edwareDataProxy, edwareGrid, edwareBreadcrumbs, edwareUtil, edwareFooter, edwareHeader, edwareDropdown) ->

  REPORT_NAME = "comparingPopulationsReport"

  LANGUAGE = "en"

  POPULATION_BAR_WIDTH = 145

  AFTER_GRID_LOAD_COMPLETE = 'jqGridLoadComplete.jqGrid'

  class ConfigBuilder
    ### Grid configuration builder. ###
    
    constructor: (template, subjects) ->
      ###
      
      ###
      output = Mustache.render(JSON.stringify(template), subjects)
      this.gridConfig = JSON.parse(output)
      this

    customize: (customView) ->
      firstColumn = this.gridConfig[0].items[0]
      firstColumn.name = customView.name
      firstColumn.options.linkUrl = customView.link
      firstColumn.options.id_name = customView.id_name
      firstColumn.sorttype = "int" if customView.name is "Grade"
      this

    build: ()->
      this.gridConfig


  class PopulationGrid

    constructor: () ->
      config = edwareDataProxy.getDataForReport REPORT_NAME, LANGUAGE
      this.initialize(config)

    initialize: (config)->
      this.config = config
      this.breadcrumbsConfigs = config.breadcrumb
      this.configTemplate = config.comparingPopulations.grid
      this.customViews = config.comparingPopulations.customViews
      this.labels = config.labels
      this.defaultColors = config.colors
      this.gridContainer = $('.gridHeight100')
      this.gridControlPanel = $(".gridControls")
      # create align button
      this.alignment = new Alignment($('.align_button'))
      # default sort
      this.sort = {
        name: 'name'
        order: 'asc'
        index: 0
      }

    sortBySubject: (sort) ->
      this.sort = $.extend(this.sort, sort)
      $('#gridTable').sortBySubject(this.sort.name, this.sort.index, this.sort.order)

    reload: (@param) ->
      # initialize variables
      this.reportType = this.getReportType(param)
      data = this.fetchData param
      this.data = data
      this.populationData = this.data.records
      this.summaryData = this.data.summary
      this.asmtSubjectsData = this.data.subjects
      #Check for colors, set to default color if it's null
      for subject, value of this.data.metadata
        if value is null
          this.data.metadata[subject] = this.defaultColors

      # process breadcrumbs
      this.renderBreadcrumbs(data.context)
      this.createGrid()
      this.updateDropdown()
      this.createHeaderAndFooter()

    createHeaderAndFooter: ()->
      edwareFooter.create('comparing_populations', this.data, this.config)
      edwareHeader.create(this.data, this.config, this.reportType)

    fetchData: (params)->
      # Determine if the report is state, district or school view"
      options =
        async: false
        method: "POST"
        params: params
      
      studentsData = undefined
      edwareDataProxy.getDatafromSource "/data/comparing_populations", options, (data)->
        studentsData = data
      studentsData

    # Based on query parameters, return the type of report that the user is requesting for
    getReportType: (params) ->
      if params['schoolGuid']
        reportType = 'school'
      else if params['districtGuid']
        reportType = 'district'
      else if params['stateCode']
        reportType = 'state'
      reportType

    createGrid: () -> 
      # Append colors to records and summary section
      # Do not format data, or get breadcrumbs if the result is empty
      preprocessor = new DataProcessor(this.summaryData[0], this.asmtSubjectsData, this.data.metadata, this.defaultColors)
      this.populationData = preprocessor.process(this.populationData)
      summaryData = preprocessor.process(this.summaryData)
      this.summaryData = this.formatSummaryData summaryData
      this.renderGrid()
      self = this
      $('#gridTable').on AFTER_GRID_LOAD_COMPLETE, ()->
        self.afterGridLoadComplete()
      self.afterGridLoadComplete()

    afterGridLoadComplete: () ->
      this.bindEvents()
      this.alignment.update()
      # Save the current sorting column and order to apply after filtering
      this.sort = $.extend this.sort, {
        order: $('#gridTable').getGridParam('sortorder')
        name: $('#gridTable').getGridParam('sortname')
      }
      
    renderGrid: () ->
      this.gridContainer.html($("<table id='gridTable'/>"))
      # Change the column name and link url based on the type of report the user is querying for
      gridConfig = new ConfigBuilder(this.configTemplate, this.asmtSubjectsData)
                             .customize(this.customViews[this.reportType])
                             .build()
      # Create compare population grid for State/District/School view
      edwareGrid.create "gridTable", gridConfig, this.populationData, this.summaryData
      this.sortBySubject this.sort
      # Display grid controls after grid renders
      this.gridControlPanel.show()

    renderBreadcrumbs: (breadcrumbsData)->
      this.breadcrumbs = new Breadcrumbs(breadcrumbsData, this.breadcrumbsConfigs, this.reportType)
      # Set the Report title depending on the report that we're looking at
      $('#content h2').html this.breadcrumbs.getReportTitle()

    bindEvents: ()->
      # Show tooltip for population bar on mouseover
      $(".progress").on
        mouseenter: ->
          e = $(this)
          e.popover
            html: true
            placement: "top"
            trigger: "manual"
            template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><div class="popover-content"><p></p></div></div></div>'
            content: ->
              e.find(".progressBar_tooltip").html() # template location: widgets/populatoinBar/template.html
          .popover("show")
        click: (e) ->
          e.preventDefault()
        mouseleave: ->
          e = $(this)
          e.popover("hide")
                
      self = this
      $('#gridTable_name').click ()->
        # Get the current sort column and reset cpop sorting dropdown if the current sort column is the first column
        self.edwareDropdown.resetAll()

    updateDropdown: ()->
      # create drop down menus
      this.edwareDropdown = this.createDropdown(this.config.comparingPopulations.customALDDropdown) if not this.edwareDropdown
      # update dropdown menus status
      this.edwareDropdown.update(this.summaryData, this.asmtSubjectsData, this.data.metadata)
          
    createDropdown: (customALDDropdown)->
      self = this
      $('.dropdownSection').edwareDropdown customALDDropdown, (subject, index)->
        self.sortBySubject subject, index

      # Format the summary data for summary row rendering purposes
    formatSummaryData: (summaryData) ->
      summaryRowName = this.breadcrumbs.getOverallSummaryName()
      data = {}
      summaryData = summaryData[0]
      for k of summaryData.results
        name = 'results.' + k + '.total'
        data[name] = summaryData.results[k].total
        
      data['subtitle'] = this.labels['reference_point']#'Reference Point'
      # Set header row to be true to indicate that it's the summary row
      data['header'] = true
      data['results'] = summaryData.results
      data['name'] = summaryRowName
      data


  class Breadcrumbs

    constructor: (@breadcrumbsData, @breadcrumbsConfigs, @reportType) ->
      # Render breadcrumbs on the page
      $('#breadcrumb').breadcrumbs(breadcrumbsData, breadcrumbsConfigs)

    getReportTitle: () ->
    # Returns report title based on the type of report
      if this.reportType is 'state'
        data = this.addApostropheS(this.breadcrumbsData.items[0].name) + ' Districts'
      else if this.reportType is 'district'
        data = this.addApostropheS(this.breadcrumbsData.items[1].name) + ' Schools'
      else if this.reportType is 'school'
        data = this.addApostropheS(this.breadcrumbsData.items[2].name) + ' Grades'
      'Comparing '+ data + ' on Math & ELA'

    # Format the summary data for summary row purposes
    getOverallSummaryName: () ->
        # Returns the overall summary row name based on the type of report
      if this.reportType is 'state'
        data = this.breadcrumbsData.items[0].name + ' District'
      else if this.reportType is 'district'
        data = this.breadcrumbsData.items[1].name + ' School'
      else if this.reportType is 'school'
        data = this.breadcrumbsData.items[2].name + ' Grade'
      'Overall ' + data + ' Summary'

    # Add an 's to a word
    addApostropheS: (word) ->
      if word.substr(word.length - 1) is "s"
        word = word + "'"
      else
        word = word + "'s"
      word


  class DataProcessor
  
    constructor: (@summaryData, @asmtSubjectsData, @colorsData, @defaultColors) ->

    # Traverse through to intervals to prepare to append color to data
    # Handle population bar alignment calculations
    process: (data) ->
      data = this.appendColors data
      data = this.appendAlignmentOffset data
      data = this.appendSortingAccessor data
      data

    appendColors: (data) ->
      for item in data
        for subject of this.asmtSubjectsData
          subjectData = item['results'][subject]
          if subjectData
            this.appendColor subjectData, this.colorsData[subject]
      data

    appendAlignmentOffset: (data) ->
      for item in data
        for subject of this.asmtSubjectsData
          subjectData = item['results'][subject]
          summary = this.summaryData.results[subject]
          if summary and subjectData
            summaryDataAlignment = summary.intervals[0].percentage + summary.intervals[1].percentage
            subjectData.alignmentLine =  (((summaryDataAlignment) * POPULATION_BAR_WIDTH) / 100) + 10 + 35
            subjectData.alignment =  (((summaryDataAlignment - 100 + subjectData.sort[1]) * POPULATION_BAR_WIDTH) / 100) + 10
      data

    appendSortingAccessor: (data) ->
      for item in data
        for subject of this.asmtSubjectsData
          subjectData = item['results'][subject]
          if subjectData
            item[subjectData.asmt_subject] = subjectData.sort
      data

      # Add color for each intervals
    appendColor: (data, colors) ->
      i = 0
      defaultColors = this.defaultColors
      intervals = data.intervals
      len = colors['colors'].length
      sort = prepareTotalPercentage data.total, len
      while i < len
        element = intervals[i]
        element = {'count': 0, 'percentage': 0} if element is undefined
        if colors and colors[i]
          element.color = colors[i]
        else
          element.color = defaultColors[i]
          
        # if percentage is less than 9 then remove the percentage text from the bar
        if element.percentage > 9
          element.showPercentage = true
        else
          element.showPercentage = false
        
        # calculate sort
        sort = calculateTotalPercentage sort, i, element.percentage
        i++
      # attach sort to data
      data.sort = sort

    # calculate percentages for each sort interval
    calculateTotalPercentage = (percentages, i, currentPercentage) ->
      k = 2
      if i is 0
        percentages[i] = currentPercentage
      else
        while k <= i
          percentages[k-1] = percentages[k-1] + currentPercentage
          k++
      percentages

    # initialize total percentages for each sort interval
    prepareTotalPercentage = (total, intervalLength) ->
      percentages = {}
      j = 0
      while j < intervalLength - 1
        # Prepopulate
        percentages[j] = 0
        j++
      percentages[intervalLength-1] = total
      percentages      


  class Alignment

    constructor: (@trigger)->
      this.aligned = false
      this.bindEvents()

    bindEvents: ()->
      # Set population bar alignment on/off
      self = this
      this.trigger.unbind('click').click () ->
        self.aligned = not self.aligned
        # toggle component
        self.trigger.toggleClass('align_on align_off')
        # update alignment
        self.update()

    update: () ->
      if this.aligned
        this.showAlignment()
      else
        this.hideAlignment()

    # Change population bar width as per alignment on/off status
    showAlignment: () ->
      $(".barContainer").addClass('alignment').removeClass('default')
      $(".populationBar").each ()->
        $this = $(this)
        $this.css "margin-left", $this.data('margin-left')

    hideAlignment: () ->
      $(".barContainer").addClass('default').removeClass('alignment')
      $(".populationBar").removeAttr('style')    

      
  PopulationGrid: PopulationGrid