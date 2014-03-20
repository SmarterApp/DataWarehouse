define [
  "jquery"
  "mustache"
  "text!YearDropdownTemplate"
  "edwarePreferences"
], ($, Mustache, YearDropdownTemplate, edwarePreferences) ->

  class AcademicYearDropdown

    constructor: (@container, @years, @callback) ->
      @initialize()
      @setDefaultOption()
      @bindEvents()

    initialize: () ->
      return if not @years
      @latestYear = @years[0].value
      output = Mustache.to_html YearDropdownTemplate,
        options: @years
      $(@container).html output
      # set latest year to reminder message
      $('.latestYear', ".reminderMessage").html @years[0].display

    setDefaultOption: () ->
      asmtYear = edwarePreferences.getAsmtYearPreference()
      if not asmtYear
        asmtYear = @years[0].value
        edwarePreferences.saveAsmtYearPreference(asmtYear)
      display = (asmtYear - 1) + " - " + asmtYear
      @setSelectedValue display, asmtYear

    setSelectedValue: (display, value) ->
      $("#selectedAcademicYear").html(display)
      $reminder =  $(".reminderMessage")
      if value is @latestYear
        $reminder.hide()
      else
        $reminder.show()

    bindEvents: () ->
      self = this
      $('li', @container).click ->
        display = $(this).data('display')
        self.setSelectedValue display
        value = $(this).data('value')
        edwarePreferences.saveAsmtYearPreference(value)
        self.callback(value)
      $('.reminderMessage a').click ->
        value = self.latestYear
        edwarePreferences.saveAsmtYearPreference(value)
        self.callback(value)



  (($) ->
    $.fn.createYearDropdown = (options, callback)->
      new AcademicYearDropdown(this, options, callback)
  ) jQuery

  AcademicYearDropdown: AcademicYearDropdown
