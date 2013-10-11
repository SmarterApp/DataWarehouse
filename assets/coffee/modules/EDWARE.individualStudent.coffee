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
  "edwareAsmtDropdown"
  "edwarePreferences"
  "edwareDisclaimer"
], ($, bootstrap, Mustache, edwareDataProxy, edwareConfidenceLevelBar, edwareClaimsBar, indivStudentReportTemplate, edwareBreadcrumbs, edwareUtil, edwareFooter, edwareHeader, edwareAsmtDropdown, edwarePreferences, edwareDisclaimer) ->
  
  # claim score weight in percentage
  claimScoreWeightArray = {
    "MATH": ["40", "40", "20", "10"],
    "ELA": ["40", "30", "20", "10"]
  }
  
  class EdwareISR
    
    constructor: () ->
      this.initialize()
      this
      
    initialize: () ->
      this.getParams()
      this.isPdf = false
      this.currentAsmtType = "Summative" 
      
      if this.params['grayscale'] is 'true'
        this.isGrayscale = true
      if this.params['pdf'] is 'true'
        this.isPdf = true
        this.currentAsmtType = this.params['asmtType'] if this.params['asmtType']
      else
        this.currentAsmtType = edwarePreferences.getAsmtPreference()

      this.configData = edwareDataProxy.getDataForReport "indivStudentReport"
      this.loadCss()
   
    getParams: () ->
      this.params = edwareUtil.getUrlParams()
   
    updateView: (asmtType) ->
      edwarePreferences.saveAsmtPreference asmtType
      this.currentAsmtType = asmtType
      this.updateDisclaimer()
      this.render asmtType
    
    updateDisclaimer: () ->
      this.disclaimer.update this.currentAsmtType
    
    fetchData: (callback) ->
      # Get individual student report data from the server
      options =
        async: true 
        method: "POST"
        params: this.params
  
      edwareDataProxy.getDatafromSource "/data/individual_student_report", options, callback
    
    loadCss: () ->
      # Show grayscale
      if this.isGrayscale
        edwareUtil.showGrayScale()
      # Load css for pdf generation
      if this.isPdf
        edwareUtil.showPdfCSS()

    load: () ->
      self = this
      this.fetchData (data) ->
        self.data  = JSON.parse(Mustache.render(JSON.stringify(data), {"labels": self.configData.labels}))
        self.defaultColors = {}
        self.defaultColors = self.configData.colors
        self.defaultGrayColors = self.configData.grayColors
        self.feedbackData = self.configData.feedback
        self.breadcrumbsConfigs = self.configData.breadcrumb
        self.reportInfo = self.configData.reportInfo
        self.data.labels = self.configData.labels
        self.legendInfo = self.configData.legendInfo
        self.asmtTypes = []
        self.dataByType = {}
        
        self.processData()
        if not self.isPdf
          self.createBreadcrumb()
          self.createDropdown()
          self.disclaimer = $('#disclaimerInfo').edwareDisclaimer self.configData.interimDisclaimer
          self.disclaimer.create()
          self.currentAsmtType = self.asmtTypes[0] if self.asmtTypes.indexOf("Summative") is -1
          self.updateDisclaimer()
          
        self.render self.currentAsmtType

    processData: () ->
      for asmt of this.data.items
        i = 0
        this.asmtTypes.push asmt
        while i < this.data.items[asmt].length
          items = this.data.items[asmt][i]
          
          # if cut points don't have background colors, then it will use default background colors
          j = 0
          while j < items.cut_point_intervals.length
            if !items.cut_point_intervals[j].bg_color
              $.extend(items.cut_point_intervals[j], defaultColors[j])
            j++
            
          if this.isGrayscale
            j = 0
            while j < items.cut_point_intervals.length
              $.extend(items.cut_point_intervals[j], this.defaultGrayColors[j])
              j++
        
          # Generate unique id for each assessment section. This is important to generate confidence level bar for each assessment
          # ex. assessmentSection0, assessmentSection1
          items.count = i
        
          # set role-based content
          items.content = this.configData.content
          
          # Select cutpoint color and background color properties for the overall score info section
          performance_level = items.cut_point_intervals[items.asmt_perf_lvl-1]
          
          # Apply text color and background color for overall score summary info section
          items.score_color = performance_level.bg_color
          items.score_text_color = performance_level.text_color
          items.score_bg_color = performance_level.bg_color
          items.score_name = performance_level.name
          
          # set level-based overall ald content
          overallALD = Mustache.render(this.configData.overall_ald[items.asmt_subject], items)
          overallALD = edwareUtil.truncateContent(overallALD, edwareUtil.getConstants("overall_ald"))
          items.overall_ald = overallALD
          
          # set psychometric_implications content
          psychometricContent = Mustache.render(this.configData.psychometric_implications[asmt][items.asmt_subject], items)
          
          # if the content is more than character limits then truncate the string and add ellipsis (...)
          psychometricContent = edwareUtil.truncateContent(psychometricContent, edwareUtil.getConstants("psychometric_characterLimits"))
          items.psychometric_implications = psychometricContent
          
          # set policy content
          grade = this.configData.policy_content[items.grade]
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
            
            claimContent = this.configData.claims[items.asmt_subject]["description"][claim.indexer]
            # if the content is more than character limits then truncate the string and add ellipsis (...)
            claimContent = edwareUtil.truncateContent(claimContent, edwareUtil.getConstants("claims_characterLimits"))
            claim.desc = claimContent
            
            claim.score_desc = this.configData.claims[items.asmt_subject]["scoreTooltip"][claim.indexer]
            
            j++
          i++
  
    createBreadcrumb: () ->
      $('#breadcrumb').breadcrumbs(this.data.context, this.breadcrumbsConfigs)

    render : (asmtType) ->
      this.data.current = this.data.items[asmtType]
      # use mustache template to display the json data    
      output = Mustache.to_html indivStudentReportTemplate, this.data     
      $("#individualStudentContent").html output
      
      this.renderClaimScoreRelativeDifference()
      
      # Generate Confidence Level bar for each assessment      
      i = 0
      while i < this.data.items[asmtType].length
        item = this.data.items[asmtType][i]       
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
      this.isrFooter = $('#footer').generateFooter('individual_student_report', this.reportInfo, {
        'legendInfo': this.legendInfo,
        'subject': this.createSampleInterval this.data.items[0], this.legendInfo.sample_intervals
      }, this.configData.labels) unless this.isrFooter
      
      this.isrHeader = edwareHeader.create(this.data, this.configData, "individual_student_report") unless this.isrHeader
     
      # Report info and legend for print version, Grayscale logo for print version
      $($("#footerLinks").html()).clone().appendTo("#print_reportInfoContent")
      if this.isGrayscale
        $(".printHeader .logo img").attr("src", "../images/smarter_printlogo_gray.png")
        
    createSampleInterval : (subject, sample_interval) ->
      # merge sample and subject information
      # the return value will be used to generate legend html page
      subject = $.extend(true, {}, subject, sample_interval)
    
    #
    # render Claim Score Relative Difference (arrows)
    #
    renderClaimScoreRelativeDifference : () ->
      i = 0
      for asmt of this.data.items
        while i < this.data.items[asmt].length
          items = this.data.items[asmt][i]
          # find grand parent element ID
          assessmentSectionId = '#assessmentSection' + i
          claims = items.claims
          j = 0
          while j < claims.length
            claim = claims[j]
            # if relative difference is 0, draw diamond on the dashed line, positive, then render uppder div
            if claim.claim_score_relative_difference == 0
              this.drawUpArrow(assessmentSectionId, claim.indexer, 0)
              this.drawDownArrow(assessmentSectionId, claim.indexer, 0)
            else if claim.claim_score_relative_difference > 0
              this.drawUpArrow(assessmentSectionId, claim.indexer, claim.claim_score_relative_difference)
            else
              this.drawDownArrow(assessmentSectionId, claim.indexer, claim.claim_score_relative_difference)
            j++
          i++
    
    # draw down triangle and arrow on target <div/>
    #  
    drawUpArrow : (assessmentSectionId, indexer, claim_score_relative_difference) ->
      # find arraw drawing box ID
      claimArrowBox = assessmentSectionId + ' #claim' + indexer + ' #content' + indexer + '_upper'
      # style for vertical bar
      bar_height = claim_score_relative_difference
      image_y_position = 100 - claim_score_relative_difference
      
      img = 'Claim_arrowhead_up'
      # style for vertical bar
      arrow_bar_class = "claim_score_arrow_bar claim_score_up_arrow_bar"
      this.drawArrow(claimArrowBox, img, image_y_position, arrow_bar_class, bar_height)
        
    #
    # draw down triangle and arrow on target <div/>
    #
    drawDownArrow : (assessmentSectionId, indexer, claim_score_relative_difference) ->
      # find arraw drawing box ID
      claimArrowBox = assessmentSectionId + ' #claim' + indexer + ' #content' + indexer + '_lower'
      img = 'Claim_arrowhead_down'
      bar_height = Math.abs(claim_score_relative_difference)
      image_y_position = Math.abs(claim_score_relative_difference)
      # style for vertical bar
      arrow_bar_class = "claim_score_arrow_bar claim_score_down_arrow_bar"
      this.drawArrow(claimArrowBox, img, image_y_position, arrow_bar_class, bar_height)
    
    # draw triangle and arrow on target <div/>
    #
    drawArrow : (claimArrowBox, triangle_img, triangle_y_position, arrow_bar_class, bar_height) ->
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

    # Create assessment type dropdown
    createDropdown : () ->
      this.asmtTypes = this.asmtTypes.sort().reverse()
      this.dropdown = $('#asmtDropdownSection').edwareAsmtDropdown this.asmtTypes, this.updateView.bind(this)
      this.dropdown.create()
      this.dropdown.setSelectedValue this.currentAsmtType     
 
  EdwareISR: EdwareISR
