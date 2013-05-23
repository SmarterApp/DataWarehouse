define [
  "jquery"
  "mustache"
  "bootstrap"
  "text!edwareFooterHtml"
], ($, Mustache, bootstrap, footerTemplate) ->
  $.fn.generateFooter = (reportName, content) ->
    self = this
    data = {}
    if reportName is 'individual_student_report'
      data['imageFileName'] = 'legend_IndivStudent.png'
    else if reportName is 'list_of_students'
      data['imageFileName'] = 'legend_ListofStudents.png'
    else if reportName is 'comparing_populations'
      data['imageFileName'] = 'legend_comparepop.png'
    
    data['report_info'] = content[reportName]
   
    output = Mustache.to_html footerTemplate, data
      
    self.html output
    createPopover()

  create = (containerId) ->
    $(containerId).generateFooter
                
  hidePopover = (id) ->
    $(id).popover("hide")
   
  createPopover = ->
    
    # Survey monkey popup
    $("#feedback").popover
      html: true
      placement: "top"
      container: "footer"
      title: ->
          '<div class="pull-right hideButton"><a class="pull-right" href="#" id="close" data-id="feedback">Hide <img src="../images/hide_x.png"></img></i></a></div><div class="lead">Feedback</div>'
      template: '<div class="popover footerPopover"><div class="arrow"></div><div class="popover-inner large"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
      content: ->
        $(".surveyMonkeyPopup").html()
        
    $("#legend").popover
      html: true
      placement: "top"
      container: "div"
      title: ->
        '<div class="pull-right hideButton"><a class="pull-right" href="#" id="close" data-id="legend">Hide <img src="../images/hide_x.png"></img></i></a></div><div class="lead">Legend</div>'
      template: '<div class="popover footerPopover"><div class="arrow"></div><div class="popover-inner large"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
      content: ->
        $(".legendPopup").html()
              
    $("#aboutReport").popover
      html: true
      placement: "top"
      container: "div"
      title: ->
        '<div class="pull-right hideButton"><a class="pull-right" href="#" id="close" data-id="aboutReport">Hide <img src="../images/hide_x.png"></img></i></a></div><div class="lead">Report Info</div>'
      template: '<div class="popover footerPopover"><div class="arrow"></div><div class="popover-inner large"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
      content: ->
        $(".aboutReportPopup").html()
        
    $("#help").popover
      html: true
      placement: "top"
      container: "div"
      title: ->
        '<div class="pull-right hideButton"><a class="pull-right" href="#" id="close" data-id="help">Hide <img src="../images/hide_x.png"></img></i></a></div><div class="lead">Help</div>'
      template: '<div class="popover footerPopover"><div class="arrow"></div><div class="popover-inner large"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
      content: ->
        $(".helpPopup").html()
     
  # Make the footer button active when associate popup opens up
  $(document).on
    click: ->
      $("#footer .nav li a.toggle").not($(this)).removeClass("active")
      $(this).toggleClass("active")
    , "#footer .nav li a.toggle"
    
  
  # Popup will close if user clicks popup hide button
  $(document).on
    click: ->
      $("#"+$(this).data("id")).popover("hide")
      $("#footer .nav li a").removeClass("active")
     , ".hideButton a"

  $(document).on
    click: ->
      url=document.URL.replace("/assets/html/","/services/pdf/")
      window.open(url, "_blank",'toolbar=0,location=0,menubar=0,status=0,resizable=yes')
    , "#print"


  create: create
