define [
  "jquery"
  "bootstrap"
  "mustache"
  "edwareDataProxy"
  "edwareGrid"
  "edwareBreadcrumbs"
  "edwareUtil"
  "edwareHeader"
  "edwarePreferences"
  "edwareConstants"
  "edwareGridStickyCompare"
  "edwareReportInfoBar"
  "edwareReportActionBar"
], ($, bootstrap, Mustache, edwareDataProxy, edwareGrid, edwareBreadcrumbs, edwareUtil, edwareHeader, edwarePreferences,  Constants, edwareStickyCompare, edwareReportInfoBar, edwareReportActionBar) ->

  LOS_HEADER_BAR_TEMPLATE = $('#edwareLOSHeaderConfidenceLevelBarTemplate').html()

  EdwareGridStickyCompare = edwareStickyCompare.EdwareGridStickyCompare

  class StudentModel

    constructor: () ->

    init: (row, assessment, dataSet) ->
      # Format student name
      row['student_full_name'] = edwareUtil.format_full_name_reverse row['student_first_name'], row['student_middle_name'], row['student_last_name']
      # This is for links in drill down
      row['params'] = {"studentGuid": row['student_guid']}
      for key, value of assessment
        cutpoint = dataSet.cutPointsData[key]
        $.extend value, cutpoint
        # display asssessment type in the tooltip title
        subjectType = dataSet.subjectsData[key]
        value.asmt_type = subjectType
        # set default colors for out of range asmt_perf_lvl
        if value.asmt_perf_lvl > value.cut_point_intervals.length
          value.score_bg_color = "#D0D0D0"
          value.score_text_color = "#000000"
        else
          value.score_bg_color = value.cut_point_intervals[value.asmt_perf_lvl - 1].bg_color
          value.score_text_color = value.cut_point_intervals[value.asmt_perf_lvl - 1].text_color
      row


  class StudentDataSet

    constructor: (@config) ->
      @cache = {}
      @asmtTypes = config.students.customViews.asmtTypes

    build: (@data) ->
      @allSubjects = "#{data.subjects.subject1}_#{data.subjects.subject2}"
      @assessmentsData  = data.assessments
      #TODO change this dummy guid to actual key for caching assessments
      @asmtGuid = 'dummyGuid'
      @subjectsData = data.subjects
      @cutPointsData = @createCutPoints()
      @columnData = @createColumns()
      @formatAssessmentsData()

    createCutPoints: () ->
      cutPointsData = @data.metadata.cutpoints
      cutPointsData = JSON.parse(Mustache.render(JSON.stringify(cutPointsData),@data))
      #if cut points don't have background colors, then it will use default background colors
      for key, items of cutPointsData
        for interval, i in items.cut_point_intervals
          if not interval.bg_color
            $.extend(interval, @config.colors[i])
      cutPointsData

    createColumns: () ->
      # Use mustache template to replace text in json config
      # Add assessments data there so we can get column names
      claimsData = JSON.parse(Mustache.render(JSON.stringify(this.data.metadata.claims), this.data))
      combinedData = $.extend(true, {}, this.data.subjects)
      combinedData.claims = claimsData
      columnData = JSON.parse(Mustache.render(JSON.stringify(@config.students), combinedData))
      columnData

    # For each subject, filter out its data
    # Also append cutpoints & colors into each assessment
    formatAssessmentsData: () ->
      asmtCache = {}
      for asmt in @asmtTypes
        asmtType = asmt['name']
        asmtCache[asmtType] ?= {}
        for assessments in @assessmentsData
          assessment = assessments[asmtType]
          continue if not assessment
          row = StudentModel::init assessments, assessment, this
          asmtCache[asmtType][@allSubjects] ?= []
          asmtCache[asmtType][@allSubjects].push row

          for key of assessment
            subjectType = @subjectsData[key]
            asmtCache[asmtType][subjectType] ?= []
            asmtCache[asmtType][subjectType].push row
      @cache[@asmtGuid] = asmtCache

    getAsmtData: (viewName)->
      # Saved asmtType and viewName
      asmt = edwarePreferences.getAsmtPreference()
      asmtGuid = @asmtGuid
      if not @cache[asmtGuid]
        #reload from server
        window.location.reload()
      asmtType = asmt.asmtType
      data = @cache[asmtGuid][asmtType][viewName]
      if data
        for item in data
          item.assessments = item[asmtType]
      data


  class StudentGrid

    constructor: (@config) ->
      @studentsDataSet = new StudentDataSet(config)
      @feedbackData = config.feedback
      @reportInfo = config.reportInfo
      @studentsConfig = config.students
      @legendInfo = config.legendInfo
      @labels = config.labels
      self = this
      @stickyCompare ?= new EdwareGridStickyCompare @labels, ()->
        self.updateView()

    reload: (params) ->
      @fetchData params
      @stickyCompare.setReportInfo Constants.REPORT_JSON_NAME.LOS, "student", params

    loadPage: (@data)->
      @studentsDataSet.build data
      @contextData = data.context
      @subjectsData = data.subjects
      @userData = data.user_info
      @grade = @contextData['items'][3]

      @renderBreadcrumbs(data.context)
      @renderReportInfo()
      @renderReportActionBar()
      @createHeaderAndFooter()

      @createGrid()
      @bindEvents()

    bindEvents: ()->
      # Show tooltip for overall score on mouseover
      $(document).on
        mouseenter: ->
          elem = $(this)
          elem.popover
            html: true
            trigger: "manual"
            container: '#content'
            placement: (tip, element) ->
              edwareUtil.popupPlacement(element, 400, 220)
            title: ->
              elem.parent().find(".losTooltip .js-popupTitle").html()
            template: '<div class="popover losPopover"><div class="arrow"></div><div class="popover-inner large"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
            content: ->
              elem.parent().find(".losTooltip").html() # html is located in widgets/EDWARE.grid.formatter performanceBar method
          .popover("show")
        click: (e) ->
          e.preventDefault()
        mouseleave: ->
          elem = $(this)
          elem.popover("hide")
      , ".asmtScore"

    createHeaderAndFooter: () ->
      this.header = edwareHeader.create(this.data, this.config, 'list_of_students') unless this.header

    fetchExportData: () ->
      this.assessmentsData

    renderBreadcrumbs: () ->
      $('#breadcrumb').breadcrumbs(@contextData, @config.breadcrumb)

    renderReportInfo: () ->
      edwareReportInfoBar.create '#infoBar',
        reportTitle: "Student Results for " + @contextData.items[3].name + " at " + @contextData.items[2].name # set school name as the page title from breadcrumb
        reportName: Constants.REPORT_NAME.LOS
        reportInfoText: @config.reportInfo
        labels: @labels
        CSVOptions: @config.CSVOptions

    renderReportActionBar: () ->
      self = this
      @config.colorsData = @studentsDataSet.cutPointsData
      @config.reportName = Constants.REPORT_NAME.LOS
      asmtTypeDropdown = @convertAsmtTypes @data.asmt_administration
      @config.asmtTypes = asmtTypeDropdown
      @actionBar ?= edwareReportActionBar.create '#actionBar', @config, () ->
        self.updateView()

    createGrid: () ->
      @updateView()
      #TODO Set asmt Subject
      subjects = []
      for key, value of @data.subjects
        subjects.push value
      edwarePreferences.saveSubjectPreference subjects

    updateView: () ->
      viewName = edwarePreferences.getAsmtPreference().asmtView
      viewName = viewName || @studentsDataSet.allSubjects
      # Add dark border color between Math and ELA section
      $('#gridWrapper').removeClass().addClass(viewName)
      this.renderGrid viewName

    fetchData: (params) ->
      self = this
      loadingData = edwareDataProxy.getDatafromSource "/data/list_of_students",
        method: "POST"
        params: params
      loadingData.done (data)->
        compiled = Mustache.render JSON.stringify(data), "labels": self.labels
        self.loadPage JSON.parse compiled

    afterGridLoadComplete: () ->
      this.stickyCompare.update()

    renderGrid: (viewName) ->
      $('#gridTable').jqGrid('GridUnload')
      asmtData = @studentsDataSet.getAsmtData(viewName)
      filedName = @studentsDataSet.columnData[viewName][0]["items"][0]["field"]
      # get filtered data and we pass in the first columns' config
      # field name for sticky chain list
      filteredInfo = this.stickyCompare.getFilteredInfo(asmtData, filedName)

      self = this
      edwareGrid.create {
        data: filteredInfo.data
        columns: @studentsDataSet.columnData[viewName]
        options:
          gridHeight: window.innerHeight - 212
          labels: this.labels
          stickyCompareEnabled: filteredInfo.enabled
          gridComplete: () ->
            self.afterGridLoadComplete()
      }
      this.renderHeaderPerfBar()

    createDisclaimer: () ->
      @disclaimer = $('.disclaimerInfo').edwareDisclaimer @config.interimDisclaimer

    renderHeaderPerfBar: () ->
      cutPointsData = @studentsDataSet.cutPointsData
      for key, items of cutPointsData
        items.bar_width = 120
        score_range = items.asmt_score_max - items.asmt_score_min

        # Calculate width for cutpoints other than first and last cutpoints
        precedence = { interval: items.asmt_score_min }
        for interval in items.cut_point_intervals
          current_span = (interval.interval - precedence.interval)
          interval.asmt_cut_point = items.bar_width * current_span / score_range
          precedence = interval
        # use mustache template to display the json data
        output = Mustache.to_html LOS_HEADER_BAR_TEMPLATE, items
        $("#"+key+"_perfBar").html(output)


    convertAsmtTypes: (asmtAdministration) ->
      selectors = {}
      for asmt in asmtAdministration
        # mapping asmt type to capitalized case
        asmt.asmt_type = Constants.ASMT_TYPE[asmt.asmt_type]
        asmt.asmt_subject_text = "#{asmt.asmt_subject} Details"
        # TODO change the combination to reflect actual link between asmts
        key = [asmt.asmt_year, asmt.asmt_type]
        selectors[key] ?= []
        selectors[key].display = "#{asmt.asmt_year} · #{this.grade.name}
          · #{asmt.asmt_type}"
        selectors[key].push asmt
      for key, asmt of selectors
        if asmt.length is 2
          # add subjects combination
          asmt.unshift
            asmt_type: asmt[0].asmt_type
            asmt_subject: "#{asmt[1].asmt_subject}_#{asmt[0].asmt_subject}"
            asmt_subject_text: "#{asmt[1].asmt_subject} & #{asmt[0].asmt_subject}"
        "display": asmt.display
        "asmt": asmt
        "hasAsmtSubject": true


  StudentGrid: StudentGrid
