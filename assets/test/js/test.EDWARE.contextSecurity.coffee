define [
  "jquery"
  "edwareContextSecurity"
], ($, contextSecurity) ->

  test_user =
    "allow_PII": true
    "allow_raw_extract": true
    "allow_assessment_extract": true
    "allow_registration_extract": true

  no_pii_msg = "No PII available"

  extractType = {
    options: [{
      value: "studentAssessment"
    }, {
      value: "studentRegistrationStatistics"
    }]
  }

  config = {
    labels: {no_pii: no_pii_msg},
    CSVOptions: {
      "extractType": extractType
    }
  }

  module "EDWARE.contextSecurity",
      setup: ->
        $("body").append "<div id='container'>
          <div id='header'></div>
          <div id='downloadMenuPopup'><li class='extract'></li><li class='csv'></li></div>
          <div id='content' class='ui-jqgrid'><a href='test.html'></a><a class='disabled' href='#'></a></div>
        </div>"

      teardown: ->
        $('#container').remove()

  test "Test context security module", ->
    ok contextSecurity, "contextSecurity should be a module"
    equal typeof(contextSecurity.apply), "function", "ContextSecurity.apply() should be a function"
    equal typeof(contextSecurity.init), "function", "ContextSecurity.init() should be a function"
    equal typeof(contextSecurity.hasPIIAccess), "function", "ContextSecurity.hasPIIAccess() should be a function"

  test "Test no pii", ->
    $anchor = $('a', '#content')
    permission = {
      PII: {
        no_control: true,
      }
    }
    contextSecurity.init permission, config
    contextSecurity.apply()
    equal $anchor.attr('href'), 'test.html'

  test "Test no pii tooltip", ->
    $anchor = $('a.disabled', '#content')
    permission = {
      PII: {
        no_control: false,
      }
    }
    contextSecurity.init permission, config
    contextSecurity.apply()
    equal $anchor.attr('href'), '#'
    $anchor.click()
    ok $('.no_pii_msg')[0], "Clicking no PII link should display a tooltip popover"

  test "Test raw extract security", ->
    permission = {
      allow_raw_extract: true
    }
    contextSecurity.init permission, config
    contextSecurity.apply()
    visible = $('.extract').is(":visible")
    ok visible, "Should display extract option"

    permission = {
      allow_raw_extract: false
    }
    contextSecurity.init permission, config
    contextSecurity.apply()
    visible = $('.extract').is(":visible")
    ok not visible, "Shouldn't display extract option"

  test "Test bulk extract security", ->
    permission = {
      allow_assessment_extract: false,
      allow_registration_extract: false
    }
    contextSecurity.init permission, config
    contextSecurity.apply()
    visible = $('.csv').is(":visible")
    ok not visible, "Shouldn't display bulk extract option"

  test "Test no registration extract", ->
    permission = {
      allow_assessment_extract: true,
      allow_registration_extract: false
    }
    extractType = {
      options: [{
        value: "studentAssessment"
      }, {
        value: "studentRegistrationStatistics"
      }]
    }
    config.CSVOptions.extractType = extractType
    contextSecurity.init permission, config
    contextSecurity.apply()
    visible = $('.csv').is(":visible")
    ok visible, "Should display bulk extract option"
    equal extractType.options.length, 1, "Should only contain assessment"
    equal extractType.options[0].value, "studentAssessment", "Should only contain assessment option"

  test "Test no assessment extract", ->
    permission = {
      allow_assessment_extract: false,
      allow_registration_extract: true
    }
    extractType = {
      options: [{
        value: "studentAssessment"
      }, {
        value: "studentRegistrationStatistics"
      }]
    }
    config.CSVOptions.extractType = extractType
    contextSecurity.init permission, config
    contextSecurity.apply()
    visible = $('.csv').is(":visible")
    ok visible, "Should display bulk extract option"
    equal extractType.options.length, 1, "Should only contain registration"
    equal extractType.options[0].value, "studentRegistrationStatistics", "Should only contain registration option"

  test "Test hasPIIAccess function", ->
    permission = {
      PII: {
        no_control: true,
        access_list: ['229']
      }
    }
    contextSecurity.init permission, config
    ok contextSecurity.hasPIIAccess('123'), "Should have permission when access is off"
    permission = {
      PII: {
        no_control: false,
        access_list: ['229']
      }
    }
    contextSecurity.init permission, config
    ok not contextSecurity.hasPIIAccess('123'), "123 Should have no permission when access is on"
    ok contextSecurity.hasPIIAccess('229'), "229 Should still have permission when access is on"
