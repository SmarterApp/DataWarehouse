define [
  "jquery"
  "mustache"
  "moment"
  "jqueryui"
  "text!CSVOptionsTemplate"
  "text!DownloadMenuTemplate"
  "edwareConstants"
  "edwareClientStorage"
  "edwarePreferences"
  "edwareExport"
  "edwareDataProxy"
], ($, Mustache, moment, jqueryui, CSVOptionsTemplate, DownloadMenuTemplate, Constants, edwareClientStorage, edwarePreferences, edwareExport, edwareDataProxy) ->

  ERROR_TEMPLATE = $(CSVOptionsTemplate).children('#ErrorMessageTemplate').html()

  SUCCESS_TEMPLATE = $(CSVOptionsTemplate).children('#SuccessMessageTemplate').html()

  INDIVIDUAL_VALID_TEMPLATE = $(CSVOptionsTemplate).children('#IndividualValidationTemplate').html()

  COMBINED_VALID_TEMPLATE = $(CSVOptionsTemplate).children('#CombinedValidationTemplate').html()

  class CSVDownloadModal

    constructor: (@container, @config) ->
      this.initialize()
      this.bindEvents()

    initialize: ()->
      this.container = $(this.container)
      output = Mustache.to_html CSVOptionsTemplate, {
        extractType: this.config['extractType']
        asmtType: this.config['asmtType']
        subject: this.config['asmtSubject']
        asmtYear: this.config['asmtYear']
        asmtState: this.config['asmtState']
        labels: this.config['labels']
      }
      this.container.html output
      this.message = $('#message', this.container)
      this.reportTypeDropdownMenu = $('ul.dropdown-menu.report_type', this.container)
      this.dropdownMenu = $('ul.dropdown-menu', this.container)
      this.checkboxMenu = $('ul.checkbox-menu', this.container)
      this.submitBtn = $('.btn-primary', this.container)
      this.asmtTypeBox = $('div#asmtType', this.container)
      this.createSpinner()
      this.selectDefault()
      this.setMainPulldownLabel()

    bindEvents: ()->
      self = this
      # prevent dropdown menu from disappearing
      $(this.reportTypeDropdownMenu).click (e) ->
        self.setMainPulldownLabel()

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

      this.submitBtn.click ()->
        # remove earlier error messages
        $('div.error', self.messages).remove()
        # validate each selection group
        invalidFields = []
        # check if button is 'Close' or 'Request'
        if $(this).data('dismiss') != 'modal'
          $('div.btn-group', self.container).each ()->
            $dropdown = $(this)
            if not self.validate($dropdown)
              $dropdown.addClass('invalid')
              invalidFields.push $dropdown.data('option-name')
          if invalidFields.length isnt 0
            self.showCombinedErrorMessage invalidFields
          else
            # disable button and all the input checkboxes
            self.disableInput()
            if self.reportType == 'studentRegistrationStatistics'
              self.sendRequest "/services/extract/student_registration_statistics"
            else
              self.sendRequest "/services/extract"

    setMainPulldownLabel: ()->
      self = this
      $('span.dropdown-display', self.reportTypeDropdownMenu.parent()).text($('input:checked', self.reportTypeDropdownMenu).attr('data-label'))
      self.reportType = $('input:checked', self.reportTypeDropdownMenu).val()
      $('tr.rpt_option.sr_rpt', self.container).toggleClass('disabled', self.reportType != 'studentRegistrationStatistics');
      $('tr.rpt_option.assm_rpt', self.container).toggleClass('disabled', self.reportType != 'studentAssessment');

    validate: ($dropdown) ->
      # check selected options
      checked = this.getSelectedOptions $dropdown
      checked.length isnt 0

    getSelectedOptions: ($dropdown)->
      # get selected option text
      checked = []
      $dropdown.find('input:checked').each () ->
        checked.push $(this).data('label')
      checked

    selectDefault: ()->
      # check first option of each dropdown
      $('ul li:nth-child(1) input',this.container).each ()->
        $(this).trigger 'click'

    sendRequest: (url)->
      params = $.extend(true, {'async': 'true'} ,this.getParams())
      # Get request time
      currentTime = moment()
      this.requestDate = currentTime.format 'MMM Do'
      this.requestTime = currentTime.format 'h:mma'

      options =
        params: params
        method: 'POST'
        redirectOnError: false

      request = edwareDataProxy.getDatafromSource url, options
      request.done this.showSuccessMessage.bind(this)
      request.fail this.showFailureMessage.bind(this)

    toDisplay: (item)->
      # convert server response to display text
      # create key and display text mapping
      configMap = {}
      for key, value of this.config
        for option in value.options
          configMap[option.value] = option.display
      for key, value of item
        item[key] = configMap[value] if configMap[value]
      item

    showCloseButton: () ->
      this.submitBtn.text 'Close'
      this.submitBtn.removeAttr 'disabled'
      this.submitBtn.attr 'data-dismiss', 'modal'

    enableInput: () ->
      this.submitBtn.removeAttr 'disabled'
      $('input:checkbox', this.container).removeAttr 'disabled'

    disableInput: () ->
      this.submitBtn.attr('disabled','disabled')
      $('input:checkbox', this.container).attr('disabled', 'disabled')

    showSuccessMessage: (response)->
      taskResponse = response['tasks'].map this.toDisplay.bind(this)
      fileName = response['fileName']
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
      params = {}
      this.dropdownMenu.each (index, param)->
        $param = $(param)
        key = $param.data('key')
        params[key] = []
        $param.find('input:checked').each ()->
          params[key].push $(this).attr('value')
      this.checkboxMenu.each (index, param)->
        $param = $(param)
        key = $param.data('key')
        params[key] = []
        $param.find('input:checked').each ()->
          params[key].push $(this).attr('value')
      storageParams = JSON.parse edwareClientStorage.filterStorage.load()
      if storageParams and storageParams['stateCode']
        params['stateCode'] = [storageParams['stateCode']]
      params

    show: () ->
      $('#CSVModal').modal()

    createSpinner: () ->
      $("#academicYear").spinner()
      date = new Date()
      $("#academicYear").val date.getFullYear()

  class DownloadMenu

    constructor: (@container, @config) ->
      this.initialize(@container)
      this.bindEvents()

    initialize: (@container) ->
      output = Mustache.to_html DownloadMenuTemplate, {}
      $(@container).html output
      this.eventHandler =
        file: this.downloadAsFile
        csv: this.sendCSVRequest
        extract: this.sendExtractRequest

    show: () ->
      $('#DownloadMenuModal').modal()

    hide: () ->
      $('#DownloadMenuModal').modal('hide')

    bindEvents: () ->
      self = this
      # bind export event
      $('.btn-primary', '#DownloadMenuModal').click ->
        # get selected option
        option = $(self.container).find('input[type="radio"]:checked').val()
        self.eventHandler[option].call(self)
        self.hide()

    downloadAsFile: () ->
      # download 508-compliant file
      $('#gridTable').edwareExport @config.reportName, @config.labels

    sendExtractRequest: () ->
      params = JSON.parse edwareClientStorage.filterStorage.load()
      # Get asmtType from session storage
      asmtType = edwarePreferences.getAsmtPreference().asmtType || Constants.ASMT_TYPE.SUMMATIVE
      params['asmtType'] = asmtType.toUpperCase()
      params['asmtSubject'] = edwarePreferences.getSubjectPreference()
      url = window.location.protocol + "//" + window.location.host + "/services/extract?sync=true&" + $.param(params, true)
      window.location = url

    sendCSVRequest: () ->
      # display file download options
      CSVDownload = new CSVDownloadModal $('.CSVDownloadContainer'), @config.CSVOptions
      CSVDownload.show()

  create = (container, config)->
    new CSVDownloadModal $(container), config

  CSVDownloadModal: CSVDownloadModal
  DownloadMenu: DownloadMenu
  create: create
