#global define
define [
  "jquery"
  "mustache"
  "cs!edwareDataProxy"
  "cs!edwareConfidenceLevelBar"
  "text!templates/individualStudent_report/individual_student_template.html"
  "text!templates/individualStudent_report/claimsInfo.html"
  "cs!edwareBreadcrumbs"
], ($, Mustache, edwareDataProxy, edwareConfidenceLevelBar, indivStudentReportTemplate, claimsInfoTemplate, edwareBreadcrumbs) ->
    
  #
  #    * Generate individual student report
  #    
  generateIndividualStudentReport = (params) ->
    
    content = {}
    
    default_cutPointColors = [{
          "text_color": "#ffffff",
          "bg_color": "#DD514C",
          "start_gradient_bg_color": "#EE5F5B",
          "end_gradient_bg_color": "#C43C35"
      }, {
          "text_color": "#000",
          "bg_color": "#e4c904",
          "start_gradient_bg_color": "#e3c703",
          "end_gradient_bg_color": "#eed909"
      }, {
          "text_color": "#ffffff",
          "bg_color": "#3b9f0a",
          "start_gradient_bg_color": "#3d9913",
          "end_gradient_bg_color": "#65b92c"
      }, {
          "text_color": "#ffffff",
          "bg_color": "#237ccb",
          "start_gradient_bg_color": "#2078ca",
          "end_gradient_bg_color": "#3a98d1"
      }]
      
    getContent "../data/content.json", (tempContent) ->
      content = tempContent
      
    edwareDataProxy.getDatafromSource "/data/individual_student_report", params, (data) ->
      
      # Apply text color and background color for overall score summary info section
      i = 0
      while i < data.items.length
        items = data.items[i]
        
        # if cut points don't have background colors, then it will use default background colors
        j = 0
        while j < items.cut_points.length
          if !items.cut_points[j].bg_color
            $.extend(items.cut_points[j], default_cutPointColors[j])
          j++
        
        # Generate unique id for each assessment section. This is important to generate confidence level bar for each assessment
        # ex. assessmentSection0, assessmentSection1
        items.count = i

        # set role-based content
        items.content = content

        # Select cutpoint color and background color properties for the overall score info section
        performance_level = items.cut_points[items.asmt_perf_lvl-1]
        

        items.score_color = performance_level.bg_color
        items.score_text_color = performance_level.text_color
        items.score_bg_color = performance_level.bg_color
        items.score_name = performance_level.name
        
        i++
        
      contextData = data.context
      
      breadcrumbsData = 
        { "items": [
          {
            name: contextData['state_name']
            link: "/assets/html/stateStudentList.html" 
          },
          {
            name: contextData['district_name']
            link: "/assets/html/districtStudentList.html" 
          },
          {
            name: contextData['school_name']
            link: "/assets/html/schoolStudentList.html" 
          },
          {
            name: contextData['grade']
            link: "/assets/html/gradeStudentList.html"
          },
          {
            name: contextData['student_name']
          }
        ]}
      
      $('#breadcrumb').breadcrumbs(breadcrumbsData)

      partials = 
        claimsInfo: claimsInfoTemplate
      
      # use mustache template to display the json data       
      output = Mustache.to_html indivStudentReportTemplate, data, partials     
      $("#individualStudentContent").html output
      
      # Generate Confidence Level bar for each assessment      
      i = 0
      while i < data.items.length
        item = data.items[i]       
        barContainer = "#assessmentSection" + i + " .confidenceLevel"
        edwareConfidenceLevelBar.create barContainer, item        
        i++

  #
  # get role-based content
  #
  getContent = (configURL, callback) ->
      content = {}
      
      return false  if configURL is "undefined" or typeof configURL is "number" or typeof configURL is "function" or typeof configURL is "object"
      
      $.ajax
        url: configURL
        dataType: "json"
        async: false
        success: (data) ->
          content = data.content

          if callback
            callback content
          else
            content

  generateIndividualStudentReport: generateIndividualStudentReport
