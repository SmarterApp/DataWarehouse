#global define
define [
  "jquery"
  "bootstrap"
  "mustache"
  "edwareDataProxy"
  "edwareConfidenceLevelBar"
  "edwareClaimsBar"
  "text!templates/individualStudent_report/individual_student_template.html"
  "edwareBreadcrumbs"
  "edwareUtil"
  "edwareFooter"
  "edwareHeader"
], ($, bootstrap, Mustache, edwareDataProxy, edwareConfidenceLevelBar, edwareClaimsBar, indivStudentReportTemplate, edwareBreadcrumbs, edwareUtil, edwareFooter, edwareHeader) ->
  
  # claim score weight in percentage
  claimScoreWeightArray = {
    "MATH": ["40", "40", "20", "10"],
    "ELA": ["40", "30", "20", "10"]
  }
  
  #
  #    * Generate individual student report
  #    
  generateIndividualStudentReport = (params) ->
    # Show grayscale
    if params['grayscale'] is 'true'
      edwareUtil.showGrayScale()
    # Load css for pdf generation
    if params['pdf'] is 'true'
      edwareUtil.showPdfCSS()
    
    content = {}
    
    configData = edwareDataProxy.getDataForReport "indivStudentReport"
      
    # Get individual student report data from the server
    options =
      async: true 
      method: "POST"
      params: params
      
    edwareDataProxy.getDatafromSource "/data/individual_student_report", options, (data) ->
      
      defaultColors = {}
      
      defaultColors = configData.colors
      defaultGrayColors = configData.grayColors
      feedbackData = configData.feedback
      breadcrumbsConfigs = configData.breadcrumb
      reportInfo = configData.reportInfo
      data.labels = configData.labels
      legendInfo = configData.legendInfo
    
      i = 0
      while i < data.items.length
        items = data.items[i]
        
        # if cut points don't have background colors, then it will use default background colors
        j = 0
        while j < items.cut_point_intervals.length
          if !items.cut_point_intervals[j].bg_color
            $.extend(items.cut_point_intervals[j], defaultColors[j])
          j++
          
        if params['grayscale'] is 'true'
          j = 0
          while j < items.cut_point_intervals.length
            $.extend(items.cut_point_intervals[j], defaultGrayColors[j])
            j++
        
        # Generate unique id for each assessment section. This is important to generate confidence level bar for each assessment
        # ex. assessmentSection0, assessmentSection1
        items.count = i

        # set role-based content
        items.content = configData.content
        

        # Select cutpoint color and background color properties for the overall score info section
        performance_level = items.cut_point_intervals[items.asmt_perf_lvl-1]
        
        # Apply text color and background color for overall score summary info section
        items.score_color = performance_level.bg_color
        items.score_text_color = performance_level.text_color
        items.score_bg_color = performance_level.bg_color
        items.score_name = performance_level.name
        
        # set level-based overall ald content
        overallALD = Mustache.render(configData.overall_ald[items.asmt_subject], items)
        overallALD = edwareUtil.truncateContent(overallALD, edwareUtil.getConstants("overall_ald"))
        items.overall_ald = overallALD
        
        # set psychometric_implications content
        psychometricContent = Mustache.render(configData.psychometric_implications[items.asmt_subject], items)
        
        # if the content is more than character limits then truncate the string and add ellipsis (...)
        psychometricContent = edwareUtil.truncateContent(psychometricContent, edwareUtil.getConstants("psychometric_characterLimits"))
        items.psychometric_implications = psychometricContent
        
        # set policy content
        grade = configData.policy_content[items.grade]
        if grade 
          if items.grade is "11"
            policyContent = grade[items.asmt_subject]
            # if the content is more than character limits then truncate the string and add ellipsis (...)
            policyContent = edwareUtil.truncateContent(policyContent, edwareUtil.getConstants("policyContent_characterLimits"))          
            items.policy_content = policyContent
          else if items.grade is "8"
            grade_asmt = grade[items.asmt_subject]
            policyContent = grade_asmt[items.asmt_perf_lvl]            
            # if the content is more than character limits then truncate the string and add ellipsis (...)
            policyContent = edwareUtil.truncateContent(policyContent, edwareUtil.getConstants("policyContent_characterLimits"))             
            items.policy_content = policyContent
        
        # Claim section
        # For less than 4 claims, width of the claim box would be 28%
        # For 4 claims, the width of the claim box would be 20%
        items.claim_box_width = "28%" if items.claims.length < 4
        items.claim_box_width = "20%" if items.claims.length == 4
        
        
        # Add claim score weight 
        j = 0
        while j < items.claims.length
          claim = items.claims[j]
          claim.assessmentUC = items.asmt_subject.toUpperCase()
          
          claim.claim_score_weight = claimScoreWeightArray[claim.assessmentUC][j]
          
          claimContent = configData.claims[items.asmt_subject]["description"][claim.indexer]
          # if the content is more than character limits then truncate the string and add ellipsis (...)
          claimContent = edwareUtil.truncateContent(claimContent, edwareUtil.getConstants("claims_characterLimits"))
          claim.desc = claimContent
          
          claim.score_desc = configData.claims[items.asmt_subject]["scoreTooltip"][claim.indexer]
          
          j++
        
        i++
        
      contextData = data.context
      $('#breadcrumb').breadcrumbs(contextData, breadcrumbsConfigs)
      
      # use mustache template to display the json data       
      output = Mustache.to_html indivStudentReportTemplate, data     
      $("#individualStudentContent").html output
      
      renderClaimScoreRelativeDifference data
      
      # Generate Confidence Level bar for each assessment      
      i = 0
      while i < data.items.length
        
        item = data.items[i]       
        barContainer = "#assessmentSection" + i + " .confidenceLevel"
        edwareConfidenceLevelBar.create item, 640, barContainer 
        
        j = 0
        while j < item.claims.length
          claim = item.claims[j]
          barContainer = "#assessmentSection" + i + " #claim" + [claim.indexer] + " .claimsBar"
          edwareClaimsBar.create claim, 300, barContainer 
          j++              
        
        
        # Set the layout for practical implications and policy content section on print version
        printAssessmentInfoContentLength = 0
        printAssessmentOtherInfo = "#assessmentSection" + i + " li.inline"
        printAssessmentOtherInfoLength = $(printAssessmentOtherInfo).length
        
        $(printAssessmentOtherInfo).each (index) ->
          printAssessmentInfoContentLength = printAssessmentInfoContentLength + $(this).html().length
        
        charLimits = 702
        if printAssessmentOtherInfoLength < 2 or printAssessmentInfoContentLength > charLimits
          $(printAssessmentOtherInfo).removeClass "inline"
        
        if printAssessmentInfoContentLength > charLimits
          assessmentInfo = "#assessmentSection" + i + " .assessmentOtherInfo"
          $(assessmentInfo + " h1").css("display", "block")
          $(".assessmentOtherInfoHeader").addClass("show").css("page-break-before", "always")
          $(assessmentInfo + " li:first-child").addClass("bottomLine")          
          
        i++
        
      # Show tooltip for claims on mouseover
      $(".arrowBox").popover
        html: true
        container: "div"
        trigger: "hover"
        placement: (tip, element) ->
          edwareUtil.popupPlacement(element, 400, 276)
        title: ->
          e = $(this)
          e.parent().parent().find(".header").find("h4").html()
        template: '<div class="popover claimsPopover"><div class="arrow"></div><div class="popover-inner large"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
        content: ->
          e = $(this)
          e.find(".claims_tooltip").html() # template location: templates/individualStudent_report/claimsInfo.html
      
      # Generate footer links
      this.isrFooter = $('#footer').generateFooter('individual_student_report', reportInfo, {
        'legendInfo': legendInfo,
        'subject': createSampleInterval data.items[0], legendInfo.sample_intervals
      }, configData.labels) unless this.isrFooter
      
      this.isrHeader = edwareHeader.create(data, configData, "individual_student_report") unless this.isrHeader
     
      # Report info and legend for print version, Grayscale logo for print version
      $($("#footerLinks").html()).clone().appendTo("#print_reportInfoContent")
      if params['grayscale'] is 'true'
        $(".printHeader .logo img").attr("src", "../images/smarter_printlogo_gray.png")

  createSampleInterval = (subject, sample_interval) ->
    # merge sample and subject information
    # the return value will be used to generate legend html page
    subject = $.extend(true, {}, subject, sample_interval)
    
  #
  # render Claim Score Relative Difference (arrows)
  #
  renderClaimScoreRelativeDifference = (data) ->
    i = 0
    while i < data.items.length
      items = data.items[i]
      # find grand parent element ID
      assessmentSectionId = '#assessmentSection' + i
      claims = items.claims
      j = 0
      while j < claims.length
        claim = claims[j]
        # if relative difference is 0, draw diamond on the dashed line, positive, then render uppder div
        if claim.claim_score_relative_difference == 0
          drawUpArrow(assessmentSectionId, claim.indexer, 0)
          drawDownArrow(assessmentSectionId, claim.indexer, 0)
        else if claim.claim_score_relative_difference > 0
          drawUpArrow(assessmentSectionId, claim.indexer, claim.claim_score_relative_difference)
        else
          drawDownArrow(assessmentSectionId, claim.indexer, claim.claim_score_relative_difference)
        j++
      i++
  #
  # draw down triangle and arrow on target <div/>
  #  
  drawUpArrow = (assessmentSectionId, indexer, claim_score_relative_difference) ->
    # find arraw drawing box ID
    claimArrowBox = assessmentSectionId + ' #claim' + indexer + ' #content' + indexer + '_upper'
    # style for vertical bar
    bar_height = claim_score_relative_difference
    image_y_position = 100 - claim_score_relative_difference
    
    img = 'Claim_arrowhead_up'
    # style for vertical bar
    arrow_bar_class = "claim_score_arrow_bar claim_score_up_arrow_bar"
    drawArrow(claimArrowBox, img, image_y_position, arrow_bar_class, bar_height)
      
  #
  # draw down triangle and arrow on target <div/>
  #
  drawDownArrow = (assessmentSectionId, indexer, claim_score_relative_difference) ->
    # find arraw drawing box ID
    claimArrowBox = assessmentSectionId + ' #claim' + indexer + ' #content' + indexer + '_lower'
    img = 'Claim_arrowhead_down'
    bar_height = Math.abs(claim_score_relative_difference)
    image_y_position = Math.abs(claim_score_relative_difference)
    # style for vertical bar
    arrow_bar_class = "claim_score_arrow_bar claim_score_down_arrow_bar"
    drawArrow(claimArrowBox, img, image_y_position, arrow_bar_class, bar_height)
  #
  # draw triangle and arrow on target <div/>
  #
  drawArrow = (claimArrowBox, triangle_img, triangle_y_position, arrow_bar_class, bar_height) ->
    claimArrowBox_width = $(claimArrowBox).width()
    claimArrowBox_height = $(claimArrowBox).height()
    image_height = 5
    arrow_bar_width = 12
    arrow_bar = $('<div/>')
    arrow_bar.addClass arrow_bar_class
    arrow_bar_center = (claimArrowBox_width/2-arrow_bar_width/2)/claimArrowBox_width*100
    
    
    
    arrow_bar.css("left", arrow_bar_center + "%")
    #"-2" to adjust height of bar perfectly.
    adjusted_bar_height = (bar_height*(claimArrowBox_height-image_height*2-2)/100)/(claimArrowBox_height-image_height*2)*100
    arrow_bar.css("height", adjusted_bar_height + "%")        
    # set Triangle image in target div
    $(claimArrowBox).addClass(triangle_img)
    $(claimArrowBox).css("background-position", "50% " + triangle_y_position + "%")
    $(claimArrowBox).append arrow_bar

  generateIndividualStudentReport: generateIndividualStudentReport
