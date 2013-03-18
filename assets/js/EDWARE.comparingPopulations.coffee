#global define
define [
  "jquery"
  "bootstrap"
  "cs!edwareDataProxy"
  "cs!edwareGrid"
  "cs!edwareBreadcrumbs"
], ($, bootstrap, edwareDataProxy, edwareGrid, edwareBreadcrumbs) ->
  #
  #    * Create Student data grid
  #    
  createPopulationGrid = (params) ->
    
    # Get school data from the server
    getPopulationData "/data/comparing_populations", params, (populationData, summaryData, asmtSubjectsData, colorsData, breadcrumbsData, user_info) ->
      
      # Read Default colors from json
      defaultColors = {}
      options =
        async: false
        method: "GET"
    
      edwareDataProxy.getDatafromSource "../data/color.json", options, (defaultColors) ->

        getColumnConfig "../data/comparingPopulations.json", (gridConfig, customViews) ->
          
          # append user_info (e.g. first and last name)
          if user_info
            $('#header .topLinks .user').html user_info._User__info.name.firstName + ' ' + user_info._User__info.name.lastName
            
          # Append colors to records and summary section
          # Do not format data, or get breadcrumbs if the result is empty
          if populationData.length > 0
            populationData = appendColorToData populationData, asmtSubjectsData, colorsData, defaultColors
            summaryData = appendColorToData summaryData, asmtSubjectsData, colorsData, defaultColors
  
            # Change the column name and link url based on the type of report the user is querying for
            reportType = getReportType(params)
            gridConfig[0].name = customViews[reportType].name
            gridConfig[0].options.linkUrl = customViews[reportType].link
            gridConfig[0].options.id_name = customViews[reportType].id_name
            
            # Render breadcrumbs on the page
            $('#breadcrumb').breadcrumbs(breadcrumbsData)
            
            # Set the Report title depending on the report that we're looking at
            reportTitle = getReportTitle(breadcrumbsData, reportType)
            $('#content h2').html 'Comparing ' + reportTitle + '\' on Math & ELA'
            
            # Format the summary data for summary row purposes
            summaryRowName = 'Overall ' + reportTitle + '\' Summary'
            summaryData = formatSummaryData(summaryData, summaryRowName)
            
          # Create compare population grid for State/District/School view
          edwareGrid.create "gridTable", gridConfig, populationData, summaryData
        
          
          # Show tooltip for population bar on mouseover
          $(document).on
            mouseenter: ->
              e = $(this)
              e.popover
                html: true
                placement: "top"
                content: ->
                  e.find(".progressBar_tooltip").html()
              .popover("show")
            mouseleave: ->
              e = $(this)
              e.popover("hide")
          , ".progress"
                  
  # Get population data from server       
  getPopulationData = (sourceURL, params, callback) ->
    
    dataArray = []
    
    return false if sourceURL is "undefined" or typeof sourceURL is "number" or typeof sourceURL is "function" or typeof sourceURL is "object"
    
    options =
      async: true
      method: "POST"
      params: params
  
    edwareDataProxy.getDatafromSource sourceURL, options, (data) ->
      populationData = data.records
      summaryData = data.summary
      asmtSubjectsData = data.subjects
      colorsData = data.colors
      breadcrumbsData = data.context
      user_info = data.user_info
      
      if callback
        callback populationData, summaryData, asmtSubjectsData, colorsData, breadcrumbsData, user_info
      else
        dataArray populationData, summaryData, asmtSubjectsData, colorsData, breadcrumbsData, user_info
      
  # Returns column configurations for population grid   
  getColumnConfig = (configURL, callback) ->
      
      dataArray = []
            
      return false  if configURL is "undefined" or typeof configURL is "number" or typeof configURL is "function" or typeof configURL is "object"
      
      options =
        async: false
        method: "GET"
      
      edwareDataProxy.getDatafromSource configURL, options, (data) ->
        schoolColumnCfgs = data.grid
        comparePopCfgs = data.customViews
         
        if callback
          callback schoolColumnCfgs, comparePopCfgs
        else
          dataArray schoolColumnCfgs, comparePopCfgs
          
  # Traverse through to intervals to prepare to append color to data
  appendColorToData = (data, asmtSubjectsData, colorsData, defaultColors) ->
    for k of asmtSubjectsData
      j = 0
      while (j < data.length)
        data[j]['results'][k].intervals = appendColor data[j]['results'][k].intervals, colorsData[k], defaultColors
        j++
    data
  
  # Add color for each intervals
  appendColor = (intervals, colorsData, defaultColors) ->
    i = 0
    len = intervals.length
    colorsData = JSON.parse(colorsData)
    while (i < len)
      element = intervals[i]
      if colorsData[i]
        element.color = colorsData[i]
      else
        element.color = defaultColors[i]
        
      # if percentage is less than 9 then remove the percentage text from the bar
      if element.percentage > 9
        element.showPercentage = true
      else
        element.showPercentage = false
      i++
    intervals
  
  # Format the summary data for summary row rendering purposes
  formatSummaryData = (summaryData, summaryRowName) ->
    data = {}
    summaryData = summaryData[0]
    for k of summaryData.results
      name = 'results.' + k + '.total'
      data[name] = summaryData.results[k].total
    data['subtitle'] = 'Reference Point'
    # Set header row to be true to indicate that it's the summary row
    data['header'] = true
    data['results'] = summaryData.results
    data['name'] = summaryRowName
    data
 
  # Returns the overall summary row name based on the type of report
  getReportTitle = (breadcrumbsData, reportType) ->
    if reportType is 'state'
      data = breadcrumbsData.items[0].name + ' Districts'
    else if reportType is 'district'
      data = breadcrumbsData.items[1].name + ' Schools'
    else if reportType is 'school'
      data = breadcrumbsData.items[2].name + ' Grades'
    data
      
  # Based on query parameters, return the type of report that the user is requesting for
  getReportType = (params) ->
    if params['schoolId']
      reportType = 'school'
    else if params['districtId']
      reportType = 'district'
    else if params['stateId']
      reportType = 'state'
    reportType
            
  createPopulationGrid: createPopulationGrid
  