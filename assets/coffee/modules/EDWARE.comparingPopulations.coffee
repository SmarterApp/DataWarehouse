#global define
define [
  "jquery"
  "bootstrap"
  "mustache"
  "edwareDataProxy"
  "edwareGrid"
  "edwareBreadcrumbs"
  "edwareUtil"
  "edwareFooter"
  "edwareFilter"
], ($, bootstrap, Mustache, edwareDataProxy, edwareGrid, edwareBreadcrumbs, edwareUtil, edwareFooter, edwareFilter) ->
  
  alignmentPercent = ""
  summaryData = []
  
  # Add header to the page
  edwareUtil.getHeader()
  
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
    
      edwareDataProxy.getDatafromSource "../data/common.json", options, (data) ->
        defaultColors = data.colors
        feedbackData = data.feedback
        breadcrumbsConfigs = data.breadcrumb
        reportInfo = data.reportInfo
        gridConfig = data.comparingPopulations.grid
        customViews = data.comparingPopulations.customViews
        customALDDropdown = data.comparingPopulations.customALDDropdown
        
        output = Mustache.render(JSON.stringify(gridConfig), asmtSubjectsData)
        gridConfig = JSON.parse(output)

        # # append user_info (e.g. first and last name)
        if user_info
          $('#header .topLinks .user').html edwareUtil.getUserName user_info
          
        # Determine if the report is state, district or school view
        reportType = getReportType(params)
        
        # Check for colors, set to default color if it's null
        for color, value of colorsData
          if value is null
            colorsData[color] = defaultColors
        
        # Append colors to records and summary section
        # Do not format data, or get breadcrumbs if the result is empty
        if populationData.length > 0
          populationData = appendColorToData populationData, asmtSubjectsData, colorsData, defaultColors
          summaryData = appendColorToData summaryData, asmtSubjectsData, colorsData, defaultColors

          # Change the column name and link url based on the type of report the user is querying for
          gridConfig[0].items[0].name = customViews[reportType].name
          gridConfig[0].items[0].options.linkUrl = customViews[reportType].link
          gridConfig[0].items[0].options.id_name = customViews[reportType].id_name
          
          if customViews[reportType].name is "Grade"
            gridConfig[0].items[0].sorttype = "int"
          
          # Render breadcrumbs on the page
          $('#breadcrumb').breadcrumbs(breadcrumbsData, breadcrumbsConfigs)
          
          # Set the Report title depending on the report that we're looking at
          reportTitle = getReportTitle(breadcrumbsData, reportType)
          $('#content h2').html reportTitle
          
          # Format the summary data for summary row purposes
          summaryRowName = getOverallSummaryName(breadcrumbsData, reportType)
          summaryData = formatSummaryData(summaryData, summaryRowName)
        
        # Create compare population grid for State/District/School view
        renderGrid gridConfig, populationData, summaryData
        
        # Generate footer
        $('#footer').generateFooter('comparing_populations', reportInfo)
        
        # # append user_info (e.g. first and last name)
        if user_info
          role = edwareUtil.getRole user_info
          uid = edwareUtil.getUid user_info
          edwareUtil.renderFeedback(role, uid, "comparing_populations_" + reportType, feedbackData)
        
        # Show tooltip for population bar on mouseover
        $(document).on
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
        , ".progress"
        
        
        # Set population bar alignment on/off
        $(".align_button").unbind('click').click ->
          $(this).toggleClass('align_off align_on')
          $("#gridTable") .trigger("reloadGrid")
        
        if $('.dropdownSection').is(':empty')
          dropdown = createDropdown asmtSubjectsData, colorsData, customALDDropdown
          $('.dropdown-toggle').dropdown()
        
        # Display grid controls after grid renders
        $(".gridControls").css("display", "block")
                
        # Extend jqgrid loadComplete event for Comparing population
        # Reset ALD sorting dropdown options and handle bar alignment styling
        $('#gridTable').bind "jqGridLoadComplete.jqGrid", (e, data) ->
           # Get the current sort column and reset cpop sorting dropdown if the current sort column is the first column
           curSortColumn = $('#gridTable').getGridParam('sortname')
           if $('#gridTable').getGridParam('colModel') and curSortColumn == $('#gridTable').getGridParam('colModel')[0].name
             # resetSortingHeader customALDDropdown;
             enableDisableSortingOnAssessments()
           formatBarAlignment();
           # Hide the drop down if data is empty
           if populationData.length is 0
             $('.dropdownSection').hide()
           else
             $('.dropdownSection').show()
           
        # Keep sorting and alignment status after regenerating grid
        $('#gridTable').trigger "jqGridLoadComplete.jqGrid"
        $('.colorsBlock input:checked').click()

  # Add filter to the page
  edwareFilter.create $('#cpopFilter'), $('.filter_label'), createPopulationGrid 

  # Render comparing population grid
  renderGrid = (gridConfig, populationData, summaryData) ->
    $("#gbox_gridTable").remove()
    $("#content .gridHeight100").append("<table id='gridTable'></table>")
    # Create compare population grid for State/District/School view
    edwareGrid.create "gridTable", gridConfig, populationData, summaryData       
  
  # Change population bar width as per alignment on/off status
  formatBarAlignment = ->
    align_button_class = $(".align_button").attr("class")
    if align_button_class.indexOf("align_on") isnt -1
      $(".populationBar").css("width", "155px")
      $(".alignmentLine").css("display", "block")
      $(".barContainer").css("margin-left", "80px")
    else
      $(".populationBar").css("width", "265px")
      $(".alignmentLine").css("display", "none")
      $(".barContainer ").css("margin-left", "15px")
  
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
  # Handle population bar alignment calculations
  appendColorToData = (data, asmtSubjectsData, colorsData, defaultColors) ->
    for k of asmtSubjectsData
      j = 0
      summaryDataAlignment = summaryData[0].results[k].intervals[0].percentage + summaryData[0].results[k].intervals[1].percentage
      while j < data.length
        appendColor data[j]['results'][k], colorsData[k], defaultColors
        
        data[j]['results'][k].alignmentLine =  (((summaryDataAlignment) * 155) / 100) + 10
        data[j]['results'][k].alignment =  (((summaryDataAlignment - 100 + data[j]['results'][k].sort[1]) * 155) / 100) + 10
        j++
    data
  
  # Add color for each intervals
  appendColor = (data, colors, defaultColors) ->
    i = 0
    intervals = data.intervals
    len = intervals.length
    sort = prepareTotalPercentage data.total, len
    while i < len
      element = intervals[i]
      if colors and colors[i]
        element.color = colors[i]
      else
        element.color = defaultColors[i]
        
      # if percentage is less than 9 then remove the percentage text from the bar
      if element.percentage > 9
        element.showPercentage = true
      else
        element.showPercentage = false
      
      # format numbers
      element.count = formatNumber element.count
      
      # calculate sort sort
      sort = calculateTotalPercentage sort, i, element.percentage
      i++
    # attach sort to data
    data.sort = sort

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
    
  # Add comma as thousand separator to numbers
  # Return 0 if parameter is undefined
  formatNumber = (num) ->
    if num then num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") else 0
  
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
 
  # Returns report title based on the type of report
  getReportTitle = (breadcrumbsData, reportType) ->
    if reportType is 'state'
      data = addApostropheS(breadcrumbsData.items[0].name) + ' Districts'
    else if reportType is 'district'
      data = addApostropheS(breadcrumbsData.items[1].name) + ' Schools'
    else if reportType is 'school'
      data = addApostropheS(breadcrumbsData.items[2].name) + ' Grades'
    'Comparing '+ data + ' on Math & ELA'
      
  # Returns the overall summary row name based on the type of report
  getOverallSummaryName = (breadcrumbsData, reportType) ->
    if reportType is 'state'
      data = breadcrumbsData.items[0].name + ' District'
    else if reportType is 'district'
      data = breadcrumbsData.items[1].name + ' School'
    else if reportType is 'school'
      data = breadcrumbsData.items[2].name + ' Grade'
    'Overall ' + data + ' Summary'
    
  # Add an 's to a word
  addApostropheS = (word) ->
    if word.substr(word.length - 1) is "s"
      word = word + "'"
    else
      word = word + "'s"
    word
    
  # Based on query parameters, return the type of report that the user is requesting for
  getReportType = (params) ->
    if params['schoolGuid']
      reportType = 'school'
    else if params['districtGuid']
      reportType = 'district'
    else if params['stateCode']
      reportType = 'state'
    reportType

  # create dropdown menu for color bars
  createDropdown = (asmtSubjectsData, colorsData, customALDDropdown) ->
    for subject, asmtSubject of asmtSubjectsData
      # get <div> object where dropdown menu will be appear
      asmtSubjectSort = $('#' + asmtSubject + "_sort")
      
      # prepare dropdown menu canvas
      if asmtSubjectSort isnt null
        #create dropdown and set to the center of each colomn
        dropdown = $("<div class='dropdown' id='" + asmtSubject + "_dropdown'></div>")

        asmtSubjectSort.css('visibility', 'hidden')
        asmtSubjectSort.siblings('span').css('visibility', 'hidden')
        
        caret = $("<a class='dropdown-toggle' id='" + asmtSubject + "_DropdownMenu' role='button' data-toggle='dropdown'><div class='dropdown_title'>" + customALDDropdown.selectSort + "</div><b class='caret'></b></a>")
        dropdown_menu = $("<ul class='dropdown-menu' role='menu' aria-labelledby='dLabel'></ul>")
        
        #prepare color bars
        i = 0
        
        #build color bars
        len = colorsData[subject].length
        while i < len
          colorBar = ''
          sortID = ''
          j = 0
          k = 0
          #last row should display "Total Students"
          sortID = asmtSubject + '_sort_' + i
          if i is len - 1
            colorBar = "<div class='totalStudents'>" + customALDDropdown.totalStudents + "</div>"
          else
            while j <= len
              #blank div for separator
              if i+1 is j
                colorBar = colorBar.concat("<div class='colorBlock'>&nbsp;</div>")
                k = 1
              #set background color
              else
                colorBar = colorBar.concat("<div class='colorBlock' style='background-color:" + colorsData[subject][j-k].bg_color + ";'>&nbsp;</div>")
              j++
          dropdown_menu.append($("<li id='" + sortID + "' class='colorsBlock'><input id='" + sortID + "_input' type='radio' name='colorBlock_sort' value='" + sortID + "' class='inputColorBlock'/><div>" + colorBar + "</div></li>"))
          i++
        dropdown.append(caret).append(dropdown_menu)
        dropdown.appendTo(".dropdownSection")
        setCenterForDropdown(asmtSubject, caret.children('.dropdown_title').width(), dropdown)
        
    # Disable sorting
    enableDisableSortingOnAssessments()
    $('.colorsBlock').click (e) ->
        # reset dropdown state
        resetSortingHeader customALDDropdown
        
        # select radio button.
        $('#'+$(this).attr('id')+'_input').attr('checked',true)
        # find subject name
        subject = this.id.substring(0,this.id.indexOf('_'))
        # obtain selected color bar and set it to table header
        asmtSubjectSort = $("#" + subject + "_sort")
        targetParentId = subject + '_DropdownMenu'
        colorBar = $(this).children('div').html()
        #set the center of table header
        targetParentElement_div = $('#' + targetParentId + ' div')
        targetParentElement_div.html(colorBar)
        setCenterForDropdown(subject, targetParentElement_div.width(), targetParentElement_div)
        
        #move sort up/down to right side
        asmtSubjectSort.parent().addClass('colorSortArrow')
        # display sort arrows
        asmtSubjectSort.siblings('span').css('visibility', 'visible')
        
        enableDisableSortingOnAssessments subject

        # Reload the grid and setting active sort column, subject is the index of the column
        $('#gridTable').sortGrid(subject, true, 'asc');
  
  resetSortingHeader = (customALDDropdown) ->
    # unselect radio button
    $('.inputColorBlock').attr('checked', false)
    $.each $(".dropdown"), (index, dropdownElement) ->
      # reset to 'Select Sort'
      # find anchor element which belongs to dropdown element.
      dropdown_a_element = $(dropdownElement).children('a')
      #find subject name
      id = $(dropdown_a_element).attr("id")
      subject = id.substring(0, id.indexOf("_"))
      asmtSubjectSort = $('#' + subject + '_sort')
      #set 'Select Sort'
      dropdown_a_element_dropdown_title = $(dropdown_a_element).children(".dropdown_title")
      dropdown_a_element_dropdown_title.html customALDDropdown.selectSort
      #set to the center of table header column
      setCenterForDropdown(subject, dropdown_a_element_dropdown_title.width(), dropdown_a_element_dropdown_title)
      # close open panel
      $(dropdownElement).removeClass('open')
      
  enableDisableSortingOnAssessments = (subject) ->
    # Enable sorting, Disable sorting in the other
    $.each $("#gridTable").getGridParam("colModel"), (index, colModel) ->
      colModel.sortable = false
      #set always enable the first column
      if index is 0
        colModel.sortable = true
      else
        if colModel.index is subject
          colModel.sortable = true

          
  setCenterForDropdown = (subject_name, width, targetElement) ->
    position = $('#' + subject_name + '_sort').parent().offset()
    parent_position = $('#' + subject_name + '_sort').closest('.gridHeight100').offset()
    position.left -= parent_position.left
    position.top -= parent_position.top
    position.left = position.left + $('#' + subject_name + '_sort').parent().width()/2-width/2
    targetElement.closest('.dropdown').css('margin-left', position.left)
    targetElement.closest('.dropdown').css('margin-top', position.top)

  
  createPopulationGrid: createPopulationGrid