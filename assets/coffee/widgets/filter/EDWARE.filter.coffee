define [
  "jquery"
  "mustache"
  "bootstrap"
  "edwareDataProxy"
  "edwareUtil"
  "edwareClientStorage"
  "text!edwareFilterTemplate"
  "edwareGrid"
  "edwareConstants"
], ($, Mustache, bootstrap, edwareDataProxy, edwareUtil, edwareClientStorage, filterTemplate, edwareGrid, Constants) ->

  # * EDWARE filter widget
  # * The module contains EDWARE filter creation method
  FILTER_CLOSE = 'edware.filter.close'

  FILTER_SUBMIT = 'edware.filter.submit'

  RESET_DROPDOWN = 'edware.filter.reset.dropdown'

  class EdwareFilter

    constructor: (@filterArea, @filterTrigger, @configs, @callback) ->
      this.loadPage()
      this.initialize()
      # bind click event
      this.bindEvents()
      return this

    initialize: ->
      # initialize variables
      this.filterArrow = $('.filterArrow', this.filterArea)
      this.filterPanel = $('.filter', this.filterArea)
      this.dropdownMenu = $('.dropdown-menu', this.filterArea)
      this.options = $('input', self.dropdownMenu)
      this.cancelButton = $('#cancel-btn', this.filterArea)
      this.submitButton = $('#submit-btn', this.filterArea)
      this.gradesFilter = $('.grade_range label input', this.filterPanel)
      this.filters = $('.filter-group', this.filterPanel)
      this.tagPanelWrapper = $('.selectedFilter_panel', this.filterArea)
      this.tagPanel = $('.filters', this.tagPanelWrapper)
      this.clearAllButton = $('.removeAllFilters', this.filterArea)
      # set session storage
      this.storage = edwareClientStorage.filterStorage
      this.template = this.configs['not_stated_message']

    loadPage: ->
      # load config from server
      output = Mustache.to_html filterTemplate, this.configs
      $(this.filterArea).html output

    bindEvents: ->
      self = this
      # subscribe filter close event
      this.filterArea.on FILTER_CLOSE, () ->
        self.closeFilter()

      # attach click event to cancel button
      this.cancelButton.click () ->
        self.cancel self

      # attach click event to submit button
      this.submitButton.click () ->
        $(self).trigger FILTER_SUBMIT

      # attach click event to filter trigger button
      $(document).off 'click', this.filterTrigger
      $(document).on 'click', this.filterTrigger, ->
        self.toggleFilterArea self

      # toggle grades checkbox effect
      this.gradesFilter.click () ->
        $(this).parent().toggleClass('blue')

      # prevent dropdown memu from disappearing
      $(this.dropdownMenu).click (e) ->
        e.stopPropagation()

      $(this.filters).on RESET_DROPDOWN, this.clearOptions

      $(this).on FILTER_SUBMIT, self.submitFilter

      # attach click event to 'Clear All' button
      $(this.clearAllButton).click ->
        self.clearAll()

      # display user selected option on dropdown
      $(this.options).click ->
        self.showOptions $(this).closest('.btn-group')

      # bind logout events
      $(document).on 'click', '#logout_button', () ->
        # clear session storage
        self.storage.clear()

      # collapse dropdown menu when focus out
      $('.filter-group-focuslost', this.filterArea).focuslost ()->
        $(this).parent().removeClass('open')

    cancel: (self) ->
      self.reset()
      self.closeFilter()

    reset: () ->
      # reset all filters
      this.filters.each () ->
        $(this).trigger RESET_DROPDOWN
      # load params from session storage
      params = this.storage.load()
      # reset params
      if params
        $.each JSON.parse(params), (key, value) ->
          filter = $('.filter-group[data-name=' + key + ']')
          if filter isnt undefined
            $('input', filter).each ->
              $(this).attr('checked', true).triggerHandler('click') if $(this).val() in value

    toggleFilterArea: (self) ->
      filterPanel = $('.filter', self.filterArea)
      filterArrow = $('.filterArrow')
      if filterPanel.is(':hidden')
         filterArrow.show()
         filterPanel.slideDown 'slow'
         # highlight trigger
         $(this.filterTrigger).addClass('active')
         edwareGrid.adjustHeight()
      else
         self.cancel self

    closeFilter: (callback) ->
      this.filterPanel.slideUp 'slow', ->
        edwareGrid.adjustHeight()
      $(this.filterTrigger).removeClass('active')
      $('a', this.filterTrigger).focus()
      noTags = $(this.tagPanel).is(':empty')
      if noTags
        filterArrow = this.filterArrow
        this.tagPanelWrapper.slideUp 'slow', ->
          filterArrow.hide()
      else
        this.tagPanelWrapper.show()
        this.filterArrow.show()
      callback() if callback

    clearAll: ->
      # clear tag panel
      $(this.tagPanel).html("")
      # reset all filters
      this.filters.each () ->
        $(this).trigger RESET_DROPDOWN
      # trigger ajax call
      $(this).trigger FILTER_SUBMIT

    submitFilter: ->
      self = this
      # display selected filters on html page
      self.createFilterBar self
      self.closeFilter ->
          self.submitAjaxCall self.callback

    createFilterBar: ->
      self = this
      # remove existing filter labels
      this.tagPanel.empty()

      # create tags for selected filter options
      this.filters.each () ->
        tag = new EdwareFilterTag($(this), self)
        $(self.tagPanel).append tag.create() unless tag.isEmpty

    submitAjaxCall: (callback) ->
      selectedValues = this.getSelectedValues()
      # construct params and send ajax call
      params = edwareUtil.getUrlParams()
      # merge selected options into param
      $.extend(params, selectedValues)
      # save param to session storage
      this.storage.save(params)
      callback params if callback

    # get parameters for ajax call
    getSelectedValues: ->
      # get fields of selected options in json format
      params = {}
      $('.filter-group').each () ->
        paramName = $(this).data('name')
        paramValues = []
        $(this).find('input:checked').each () ->
          paramValues.push String(this.value)
        params[paramName] = paramValues if paramValues.length > 0
      params

    clearOptions: ->
      checkBox = $(this).find("input:checked")
      checkBox.attr("checked", false)
      checkBox.parent().toggleClass('blue')
      # reset dropdown component text
      $(this).find('.selected').remove()

    # show selected options on dropdown component
    showOptions: (buttonGroup) ->
      text = this.getSelectedOptionText buttonGroup
      # remove existing text
      button = $('button', buttonGroup)
      $('.selected', button).remove()
      # compute width property, subtract 20px for margin
      textLength = this.computeTextWidth button
      $('.display', button).append $('<div class="selected">').css('width', textLength).text(text)

    # get selected option text as string separated by comma
    getSelectedOptionText: (buttonGroup) ->
      delimiter = ', '
      text =  $('input:checked', buttonGroup).map(() ->
                    $(this).data('label')
              ).get().join(delimiter)
      if text isnt "" then '[' + text + ']'  else ""

    # compute width property for text
    computeTextWidth: (button) ->
      # compute display text width this way because $().width() doesn't work somehow
      displayWidth = $('.display', button).text().length * 10
      width = $(button).width() - displayWidth - 35
      # keep minimum width 30px
      if width > 30 then width else 30

    loadReport: (params) ->
      this.reset()
      this.submitFilter()

    update: (data) ->
      self = this
      total = data['total']
      $('.filter-wrapper').each () ->
        filterName = $(this).data('name')
        count = data[filterName]
        percentage = Math.round(count * 100.0 / total)
        if percentage > 0
          # show percentage
          self.updatePercentage(this, percentage)
        else
          # hide percentage
          self.hidePercentage(this)

    hidePercentage: (filter) ->
      $('p.not_stated', filter).remove()


    updatePercentage: (filter, percentage) ->
      output = Mustache.to_html this.template, { 'percentage': percentage }
      $('p.not_stated', filter).html output


  class EdwareFilterTag

    constructor: (@dropdown, @filter) ->
      this.init()
      this.bindEvents()

    create: ->
      this.label

    init: ->
      param = {}
      param.display = this.dropdown.data('display')
      param.values = []
      this.dropdown.find('input:checked').each () ->
        label = $(this).data('label').toString()
        # remove asterisk * from the label
        label = label.replace /\*$/, ""
        param.values.push label
      this.label = this.generateLabel param
      this.isEmpty = (param.values.length is 0)

    generateLabel: (data) ->
      template = "<span class='selectedFilterGroup'>
        <span aria-hidden='true' id='aria-{{display}}'>
          <span>{{display}}: </span>
          {{#values}}
            <span>{{.}}</span><span class='seperator'>, </span>
          {{/values}}
        </span>
        <a href='#' class='removeIcon' role='button'
          aria-labelledby='aria-filtered-by aria-{{display}} aria-filter-remove'/>
      </span>"
      output = Mustache.to_html(template, data)
      $(output)

    bindEvents: ->
      self = this
      # attach click event on remove icon
      $('.removeIcon', this.label).click () ->
        self.remove self

    # remove individual filters
    remove: (self) ->
      #remove label
      $(self.label).remove()
      # reset filter
      $(self.dropdown).trigger RESET_DROPDOWN
      # trigger ajax call
      $(self.filter).trigger FILTER_SUBMIT


  createFilter = (filters) ->

    match = {
      demographics : (assessment) ->
        # TODO: may need refactoring
        for filterName, filterValue of filters
          # do not check other attributes
          if not $.isArray(filterValue)
            continue
          if filterName in ['studentGroupId', 'validity', 'complete']
            continue
          if filterName.substr(0, 5) isnt 'group' and filterName.substr(0, 5) isnt 'grade' # do not check grouping filters
            return false if assessment.demographic[filterName] not in filterValue
        return true

      grouping: (subject) ->
        if not filters.studentGroupId
          return true
        for groupId in filters.studentGroupId
          if groupId in subject.group
            return true
        return false

      complete: (subject) ->
        # return true to show the record, and false to hide
        result = false
        return true if not filters.complete
        for filter in filters.complete
            if filter == "Y"
                result = result || subject.complete == true
            if filter == "N"
                result = result || subject.complete == false
        return result

      validity: (subject) ->
        result = false
        return true if not filters.validity
        for filter in filters.validity
            if filter == "NS" #Non-standard
                result = result || (subject.administration_condition == null || subject.administration_condition == "NS")
            if filter == "SD" #Standard
                result = result || subject.administration_condition == "SD"
            if filter == "VA"
                result = result || (subject.administration_condition == null || subject.administration_condition == "VA")
            if filter == "IN"
                result = result || subject.administration_condition == "IN"
        return result
    }

    IABFilter = (data) ->
      # no filters applied
      return data if not filters

      for asmtType, studentList of data.assessments
        for studentId, assessment of studentList
          if not match.demographics(assessment)
            assessment.hide = true
            continue
          else
            assessment.hide = false
          # check grouping filters
          if not match.grouping(assessment)
            assessment.hide = true
          else
            assessment.hide = false
      data

    FAOFilter = (data) ->
      # no filters applied
      return data if not filters
      for asmtType, studentGroupByType of data.assessments
        for studentId, asmtList of studentGroupByType
          for asmtByDate in asmtList
            for asmtDate, assessment of asmtByDate
              assessment.hide = if not match.demographics(assessment) then true else false
              # check grouping and complete filters
              for subject of data.subjects
                asmt_subject = assessment[subject]
                continue if not asmt_subject
                asmt_subject.hide = if not match.grouping(asmt_subject) then true else false
                asmt_subject.hide = asmt_subject.hide || !match.complete(asmt_subject)
                asmt_subject.hide = asmt_subject.hide || !match.validity(asmt_subject)
      data

    return (asmtType) ->
      if asmtType is Constants.ASMT_TYPE.IAB
        return IABFilter
      else
        return FAOFilter


  #
  #    *  EDWARE Filter plugin
  #    *  @param filterHook - Panel config data

  #    *  @param callback - callback function, triggered by click event on apply button
  #    *  Example: $("#table1").edwareFilter(filterTrigger, callbackFunction)
  #
  (($)->
    $.fn.edwareFilter = (filterTrigger, configs, callback) ->
      new EdwareFilter($(this), filterTrigger, configs, callback)
  ) jQuery

  createFilter: createFilter
