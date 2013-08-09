define [
  'jquery'
  'mustache'
], ($, Mustache) ->
  #
  # * EDWARE util
  # * Handles constants, reusable or common methods required by other EDWARE javascript files
  # 
  
  #global $ window 
  
  constants = 
      overall_ald: 275
      psychometric_characterLimits: 256
      policyContent_characterLimits: 256
      claims_characterLimits: 140
      
  getConstants = (value) ->
    constants[value]
      
  displayErrorMessage = (error) ->
    
    if error isnt ""
      $("#errorMessage").show().html(error)
    else
      $("#errorMessage").hide()
      
    
  getUrlParams = ->
    params = {}
    window.location.search.replace /[?&]+([^=&]+)=([^&]*)/g, (str, key, value) ->
      params[key] = value
  
    params
  
  # Given an user_info object, return the one role of that user from the list
  getRole = (userInfo) ->
    # roles is a list, for beta, we can assume we only have 1 role
    userInfo._User__info.roles[0].toUpperCase()
  
  # Given an user_info object, return the first and last name of the user
  getUserName = (userInfo) ->
    userInfo._User__info.name.firstName + ' ' + userInfo._User__info.name.lastName
    
  # Given an user_info object, return the uid
  getUid = (userInfo) ->
    userInfo._User__info.uid

  format_full_name_reverse = (first_name, middle_name, last_name) ->
    if (middle_name && middle_name.length > 0)
        middle_init = middle_name[0] + '.'
    else
        middle_init = ''
    return "#{last_name}, #{first_name} #{middle_init}".replace '  ', ' '
    
  # truncate the content and add ellipsis "..." if content is more than character limits
  truncateContent = (content, characterLimits)->
    if content.length > characterLimits
      content = content.substr(0, characterLimits)
      
      # ignore characters after the last word
      content = content.substr(0, content.lastIndexOf(' ') + 1) + "..."
      
    content
    
  # Create Survey Monkey iframe based on the role, report.  Uses uid to append to the URL to identify the user that submits the survey
  renderFeedback = (role, uid, reportName, feedbackMapping) ->
    feedbackdata = {}
    if role of feedbackMapping
      if reportName of feedbackMapping[role]
        feedbackdata.param = feedbackMapping[role][reportName]
        feedbackdata.uid = uid
        
        # Render iframe with all other assets are loaded
        $(document).ready ->
          template = "<iframe id='sm_e_s' width='600' height='300' frameborder='0' allowtransparency='true' style='border:0px;padding-bottom:4px;' src='https://www.surveymonkey.com/s.aspx?sm={{param}}&c={{uid}}'></iframe>"
          output = Mustache.to_html template, feedbackdata
          $("#surveyMonkeyInfo").html output
          
          
  # Set the popup position to left, right, top, bottom
  popupPlacement = (element, popupWidth, popupHeight)->
    isWithinBounds = (elementPosition) ->
        boundTop < elementPosition.top and boundLeft < elementPosition.left and boundRight > (elementPosition.left + actualWidth) and boundBottom > (elementPosition.top + actualHeight)
    
    $element = $(element)
    pos = $.extend({}, $element.offset(),
      width: element.offsetWidth
      height: element.offsetHeight
    )
    actualWidth = popupWidth
    actualHeight = popupHeight
    boundTop = $(document).scrollTop()
    boundLeft = $(document).scrollLeft()
    boundRight = boundLeft + $(window).width()
    boundBottom = boundTop + $(window).height()
    elementAbove =
      top: pos.top - actualHeight
      left: pos.left + pos.width / 2 - actualWidth / 2
  
    elementBelow =
      top: pos.top + pos.height
      left: pos.left + pos.width / 2 - actualWidth / 2
  
    elementLeft =
      top: pos.top + pos.height / 2 - actualHeight / 2
      left: pos.left - actualWidth
  
    elementRight =
      top: pos.top + pos.height / 2 - actualHeight / 2
      left: pos.left + pos.width
  
    above = isWithinBounds(elementAbove)
    below = isWithinBounds(elementBelow)
    left = isWithinBounds(elementLeft)
    right = isWithinBounds(elementRight)
    if above
      "top"
    else
      if below
        "bottom"
      else
        if left
          "left"
        else
          if right
            "right"
          else
            "left"
            
            
  getHeader = ->
    header_html = "<div id='logo'>" +
                  "<img src='../images/smarterHeader_logo.png' alt='logo' height='36' width='112'>" +
                  "</div>" +
                  "<div id='headerTitle'>Reporting Beta UAT - DRAFT SYSTEM</div>" + 
                  "<div class='topLinks'>" +
                  "<span id='headerUser' class='user'></span><span class='seperator'>|</span><span id='headerLogout'><a href='/logout' target='iframe_logout'>Log Out</a></span>" +
                  "</div>" +
                  "<!--This iframe is used for logout redirect.  Do not remove it.-->" +
                  "<iframe frameborder='0' height='0px' width='0px' name='iframe_logout'></iframe>"
    $("#header").html(header_html)


  showGrayScale = ->
    $('head').append("<link rel='stylesheet' type='text/css' href='../css/grayscale.css' />");
    
  showPdfCSS = ->
    $('head').append("<link rel='stylesheet' type='text/css' href='../css/pdf.css' />");

  # Add comma as thousand separator to numbers
  # Return 0 if parameter is undefined
  formatNumber = (num) ->
    if num then num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") else 0

  getConstants: getConstants
  displayErrorMessage: displayErrorMessage
  getUrlParams: getUrlParams 
  getRole: getRole
  getUserName: getUserName
  getUid: getUid
  truncateContent: truncateContent
  renderFeedback: renderFeedback
  popupPlacement: popupPlacement
  getHeader: getHeader
  format_full_name_reverse: format_full_name_reverse
  showGrayScale : showGrayScale
  showPdfCSS : showPdfCSS
  formatNumber: formatNumber