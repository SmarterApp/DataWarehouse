define [
  "jquery"
  "bootstrap"
  "mustache"
  "moment"
  "text!CSVOptionsTemplate"
  "text!DownloadMenuTemplate"
  "text!PDFOptionsTemplate"
  "text!SuccessTemplate"
  "text!FailureTemplate"
  "text!NoDataTemplate"
  "edwareConstants"
  "edwareClientStorage"
  "edwarePreferences"
  "edwareExport"
  "edwareDataProxy"
  "edwareUtil"
  "edwareModal"
  "edwareEvents"
], ($, bootstrap, Mustache, moment, CSVOptionsTemplate, DownloadMenuTemplate, PDFOptionsTemplate, SuccessTemplate, FailureTemplate, NoDataTemplate, Constants, edwareClientStorage, edwarePreferences, edwareExport, edwareDataProxy, edwareUtil, edwareModal, edwareEvents) ->

  REQUEST_ENDPOINT = {
    "registrationStatistics": "/services/extract/student_registration_statistics",
    "studentAssessment": "/services/extract",
    "completionStatistics": "/services/extract/student_assessment_completion"
    "rawXML": "/some/dummy/url"
    "itemLevel": "/some/dummy/url"
  }

  showFailureMessage = (response) ->
    @hide()
    $('#DownloadResponseContainer').html Mustache.to_html FailureTemplate, {
      labels: @config.labels
      options: @config.ExportOptions
    }
    $('#DownloadFailureModal').edwareModal
      keepLastFocus: true

  showSuccessMessage = (response) ->
    @hide()
    download_url = response["download_url"]
    $('#DownloadResponseContainer').html Mustache.to_html SuccessTemplate, {
      labels: @config.labels
      options: @config.ExportOptions
      download_url: download_url
    }
    $('#DownloadSuccessModal').edwareModal
      keepLastFocus: true

  class StateDownloadModal

    constructor: (@container, @config, @reportParamCallback) ->
      @initialize()
      @bindEvents()

    initialize: ()->
      output = Mustache.to_html CSVOptionsTemplate, {
        extractType: this.config.extractType
        asmtType: this.config['asmtType']
        subject: this.config['asmtSubject']
        academicYear: this.config['academicYear']
        registrationAcademicYear: this.config['registrationAcademicYear']
        asmtState: this.config['asmtState']
        labels: this.config['labels']
        grade: this.config['grade']
        options: this.config.ExportOptions
      }
      this.container.html output
      this.dropdownMenu = $('ul.dropdown-menu', this.container)
      this.checkboxMenu = $('ul.checkbox-menu', this.container)
      this.submitBtn = $('.edware-btn-primary', this.container)
      this.asmtTypeBox = $('div#asmtType', this.container)
      this.selectDefault()
      this.fetchParams =
        completionStatistics: this.getSACParams
        registrationStatistics: this.getSRSParams
        rawXML: this.getRawExtractParams
        itemLevel: this.getRawExtractParams

    bindEvents: ()->
      self = this
      # show or hide componenets on page according export type
      $('.extractType input', @container).click (e) ->
        self.extractType = $(this).attr('value')
        $('#StateDownloadModal .modal-body').removeClass().addClass("#{self.extractType} modal-body")

      # set up academic years
      $('ul.edware-dropdown-menu li', @container).click (e)->
        $this = $(this)
        display = $this.data('label')
        value = $this.data('value')
        $dropdown = $this.closest('.btn-group')
        $dropdown.find('.dropdown-menu').attr('data-value', value)
        # display selected option
        $dropdown.find('.dropdown-display').html display
        $dropdown.removeClass 'open'
      .keypress (e) ->
        $(this).click() if e.keyCode is 13

      $('input:checkbox', this.container).click (e)->
        $this = $(this)
        $dropdown = $this.closest('.btn-group')
        # remove earlier error messages
        $('div.error', self.messages).remove()
        if not self.validate($dropdown)
          $dropdown.addClass('invalid')
          self.showNoneEmptyMessage $dropdown.data('option-name')
        else
          $dropdown.removeClass('invalid')

      # collapse dropdown menu when focus out
      $('.btn-group', this.container).focuslost ()->
        $(this).removeClass('open')

      this.submitBtn.click ()->
        # disable button and all the input checkboxes
        self.disableInput()
        # get parameters
        params = self.fetchParams[self.extractType].call(self)
        self.sendRequest REQUEST_ENDPOINT[self.extractType], params

    getSACParams: () ->
      academicYear = $('#academicYear').data('value')
      return {
        "extractType": ["studentAssessmentCompletion"]
        "academicYear": [ academicYear]
      }

    getSRSParams: () ->
      academicYear = $('#registrationAcademicYear').data('value')
      return {
        "extractType": ["studentRegistrationStatistics"]
        "academicYear": [ academicYear ]
      }

    getRawExtractParams: () ->
      academicYear = $('#academicYear').data('value')
      grade = $('#grade').data('value')
      asmtSubject = $('input[name="asmtSubject"]:checked').val()
      asmtType = $('input[name="asmtType"]:checked').val()
      return {
        "extractType": ["studentRegistrationStatistics"]
        "academicYear": [ academicYear ]
        "asmtSubject": [ asmtSubject ]
        "asmtType": [ asmtType ]
      }

    getSelectedOptions: ($dropdown)->
      # get selected option text
      checked = []
      $dropdown.find('input:checked').each () ->
        checked.push $(this).data('label')
      optionValue = $dropdown.find('.dropdown-menu').data('value')
      if optionValue
        checked.push optionValue
      checked

    selectDefault: ()->
      # check first option of each dropdown
      $('ul li:nth-child(1) input',this.container).each ()->
        $(this).trigger 'click'

    sendRequest: (url, params)->
      params = $.extend(true, params, this.getParams())

      # Get request time
      currentTime = moment()
      this.requestDate = currentTime.format 'MMM Do'
      this.requestTime = currentTime.format 'h:mma'

      options =
        params: params
        method: 'POST'
        redirectOnError: false

      request = edwareDataProxy.getDatafromSource url, options
      request.done showSuccessMessage.bind(this)
      request.fail showFailureMessage.bind(this)

    showCloseButton: () ->
      this.submitBtn.text 'Close'
      this.submitBtn.removeAttr 'disabled'
      this.submitBtn.attr 'data-dismiss', 'modal'

    hide: () ->
      $('#StateDownloadModal').edwareModal('hide')
      this.submitBtn.removeAttr 'disabled'
      $('input:checkbox', this.container).removeAttr 'disabled'
      $('.btn-extract-academic-year').attr('disabled', false)
      $('button.report_type', self.container).removeAttr 'disabled'

    disableInput: () ->
      this.submitBtn.attr('disabled','disabled')
      $('input:checkbox', this.container).attr('disabled', 'disabled')
      $('.btn-extract-academic-year').attr('disabled', true)
      $('button.report_type', self.container).attr('disabled', 'disabled')

    showSuccessMessage: (response)->
      taskResponse = response['tasks'].map this.toDisplay.bind(this)
      fileName = response['fileName']

      downloadUrl = response['download_url']
      success = taskResponse.filter (item)->
        item['status'] is 'ok'
      failure = taskResponse.filter (item)->
        item['status'] is 'fail'
      if success.length > 0
        this.showCloseButton()
      else
        this.enableInput()

      this.message.html Mustache.to_html SUCCESS_TEMPLATE, {
        requestTime: this.requestTime
        requestDate: this.requestDate
        fileName: fileName
        downloadUrl: downloadUrl
        testName: TEST_NAME[this.reportType]
        # success messages
        success: success
        singleSuccess: success.length == 1
        multipleSuccess: success.length > 1
        # failure messages
        failure: failure
        singleFailure: failure.length == 1
        multipleFailure: failure.length > 1
      }

    showFailureMessage: (response)->
      this.enableInput()
      errorMessage = Mustache.to_html ERROR_TEMPLATE, {
        response: response
      }
      this.message.append errorMessage
      this.asmtTypeBox.addClass('invalid')

    showNoneEmptyMessage: (optionName)->
      validationMsg = Mustache.to_html INDIVIDUAL_VALID_TEMPLATE, {
        optionName: optionName.toLowerCase()
      }
      this.message.append validationMsg

    showCombinedErrorMessage: (optionNames)->
      validationMsg = Mustache.to_html COMBINED_VALID_TEMPLATE, {
        optionNames: optionNames
      }
      this.message.append validationMsg

    getParams: ()->
      params = {'async': 'true'}

      storageParams = JSON.parse edwareClientStorage.filterStorage.load()
      if storageParams and storageParams['stateCode']
        params['stateCode'] = [storageParams['stateCode']]

      params

    show: () ->
      $('#StateDownloadModal').edwareModal
        keepLastFocus: true


  class PDFModal

    constructor: (@container, @config) ->
      self = this
      loadingLanguage = edwareDataProxy.getDatafromSource "../data/languages.json"
      loadingLanguage.done (data)->
        languages = for key, value of data.languages
          { key:key, value: value }
        self.initialize languages
        self.bindEvents()
        self.show()

    initialize: (languages) ->
      output = Mustache.to_html PDFOptionsTemplate,
        labels: @config.labels
        languages: languages
        options: @config.ExportOptions
      @container.html output

    bindEvents: () ->
      self = this
      $('#bulkprint').on 'click', ->
        $(this).attr('disabled', 'disabled')
        self.sendPDFRequest()

      # check English by default
      $('input#en').attr('checked', 'checked')

    getParams: () ->
      params = edwarePreferences.getFilters()
      asmt = edwarePreferences.getAsmtPreference()
      # backend expects asmt grades as a list
      grade = params['asmtGrade']
      if grade
        params['asmtGrade'] = [ grade ]
      else
        params['asmtGrade'] = undefined
      params["effectiveDate"] = asmt.effectiveDate
      params["asmtType"] = asmt.asmtType || 'Summative'
      params["asmtYear"] = edwarePreferences.getAsmtYearPreference()

      language = @container.find('input[name="language"]:checked').val()
      # color or grayscale
      mode = @container.find('input[name="color"]:checked').val()
      params["lang"] = language
      params["mode"] = mode
      params

    sendPDFRequest: () ->
      params = @config.getReportParams()
      params = $.extend(@getParams(), params)
      request = edwareDataProxy.sendBulkPDFRequest params
      request.done showSuccessMessage.bind(this)
      request.fail showFailureMessage.bind(this)

    show: () ->
      $('#PDFModal').edwareModal
        keepLastFocus: true

    hide: () ->
      $('#bulkprint').removeAttr('disabled')
      $('#PDFModal').edwareModal('hide')

  class DownloadMenu

    constructor: (@container, @config) ->
      @reportType = @config.reportType
      this.initialize(@container)
      this.bindEvents()

    disableInvisibleButtons: () ->
      $('input[type="radio"]:not(:visible)', @container).attr('disabled', 'disabled')

    initialize: (@container) ->
      output = Mustache.to_html DownloadMenuTemplate, {
        reportType: @reportType
        labels: this.config['labels']
        options: this.config.ExportOptions
      }
      $(@container).html output
      this.eventHandler =
        file: this.downloadAsFile
        csv: this.sendCSVRequest
        extract: this.sendExtractRequest
        pdf: this.printPDF

    show: () ->
      $('#DownloadMenuModal').edwareModal()

    hide: () ->
      $('#exportButton').removeAttr('disabled')
      $('#DownloadMenuModal').edwareModal('hide')

    bindEvents: () ->
      self = this
      # bind export event
      $('.btn-primary', '#DownloadMenuModal').click ->
        # disable button to avoid user click twice
        $('#exportButton').attr('disabled', 'disabled')
        # get selected option
        option = $(self.container).find('input[type="radio"]:checked').val()
        self.eventHandler[option].call(self)
      $('#DownloadMenuModal').on 'shown', ->
        self.disableInvisibleButtons()

    downloadAsFile: () ->
      # download 508-compliant file
      $('#gridTable').edwareExport @config.reportName, @config.labels
      @hide()

    getParams: ()->
      # extract both Math and ELA summative results
      params = {}
      params['asmtSubject'] = Constants.SUBJECTS
      params['asmtType'] = ['SUMMATIVE']
      asmtYear = edwarePreferences.getAsmtYearPreference()
      params["asmtYear"] =[asmtYear.toString()]
      params['extractType'] = ['studentAssessment']

      storageParams = JSON.parse edwareClientStorage.filterStorage.load()
      if storageParams and storageParams['stateCode']
        params['stateCode'] = [storageParams['stateCode']]

      if storageParams and storageParams['districtGuid']
        params['districtGuid'] = [storageParams['districtGuid']]

      params

    sendAsyncExtractRequest: () ->
      # extract Math and ELA summative assessment data
      params = $.extend(true, {'async': 'true'}, this.getParams())
      # Get request time
      currentTime = moment()
      this.requestDate = currentTime.format 'MMM Do'
      this.requestTime = currentTime.format 'h:mma'

      options =
        params: params
        method: 'POST'
        redirectOnError: false

      request = edwareDataProxy.getDatafromSource REQUEST_ENDPOINT["studentAssessment"], options
      request.done showSuccessMessage.bind(this)
      request.fail showFailureMessage.bind(this)

    sendExtractRequest: () ->
      # perform asynchronous extract on state and distrct level
      if @reportType is Constants.REPORT_TYPE.STATE or @reportType is Constants.REPORT_TYPE.DISTRICT
        this.sendAsyncExtractRequest()
      else
        # perform synchronous extract on school and grade level
        this.sendSyncExtractRequest()
        this.hide()

    sendSyncExtractRequest: () ->
      values = JSON.parse edwareClientStorage.filterStorage.load()
      # Get asmtType from session storage
      asmtType = edwarePreferences.getAsmtPreference().asmtType || Constants.ASMT_TYPE.SUMMATIVE
      # Get filters
      params = edwarePreferences.getFilters()
      # Get sticky compared rows if any
      params = $.extend(@config.getReportParams(), params)
      params['stateCode'] = values['stateCode']
      params['districtGuid'] = values['districtGuid']
      params['schoolGuid'] = values['schoolGuid']
      params['asmtGrade'] = values['asmtGrade'] if values['asmtGrade']
      params['asmtType'] = asmtType.toUpperCase()
      params['asmtSubject'] = edwarePreferences.getSubjectPreference()
      params['asmtYear'] = edwarePreferences.getAsmtYearPreference()
      url = window.location.protocol + "//" + window.location.host + "/services/extract?sync=true&" + $.param(params, true)
      window.location = url

    sendCSVRequest: () ->
      @hide()
      CSVOptions = @config.CSVOptions
      CSVOptions.labels = @config.labels
      CSVOptions.ExportOptions = @config.ExportOptions
      reportType = @config.reportType
      reportParamsCallback = @config.getReportParams

      # construct CSVDownload modal
      loadingData = fetchData @config.param
      loadingData.done (data)->
        # merge academic years to JSON config
        years = edwareUtil.getAcademicYears data.asmt_period_year
        studentRegYears = edwareUtil.getAcademicYears data.studentRegAcademicYear
        CSVOptions.academicYear.options = years if years
        CSVOptions.registrationAcademicYear.options = studentRegYears if studentRegYears
        # display file download options
        CSVDownload = new StateDownloadModal $('.CSVDownloadContainer'), CSVOptions, reportParamsCallback
        CSVDownload.show()

    printPDF: () ->
      @hide()
      hasData = $('#gridTable').text() isnt ''
      if not hasData
        # display warning message and stop
        @displayWarningMessage()
      else
        @PDFOptionsModal ?= new PDFModal $('.PrintContainer'), @config
        @PDFOptionsModal.show()

    displayWarningMessage: () ->
      output = Mustache.to_html NoDataTemplate,
        labels: @config.labels
        options: @config.ExportOptions
      $('#DownloadResponseContainer').html output
      $('#DownloadFailureModal').edwareModal
        keepLastFocus: true

    fetchData = (params)->
      options =
        method: "POST"
        params: params
        redirectOnError: false
      edwareDataProxy.getDatafromSource "/data/academic_year", options

  create = (container, reportType, config, reportParamCallback)->
    new StateDownloadModal $(container), reportType, config, reportParamCallback

  StateDownloadModal: StateDownloadModal
  DownloadMenu: DownloadMenu
  create: create
