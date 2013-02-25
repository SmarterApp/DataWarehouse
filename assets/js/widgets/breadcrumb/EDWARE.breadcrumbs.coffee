define [
  'jquery'
  "mustache"
  "text!widgets/breadcrumb/template.html"
], 
  #
  # * EDWARE breadcrumbs
  # * The module contains EDWARE breadcrumbs plugin and breadcrumbs creation method
  # 
    
    #
    #    *  EDWARE Breadcrumbs plugin
    #    *  @param data
    #    *  Example: $("#table1").edwareBreadcrumbs(data)
    #    

    ($, Mustache, template) ->
      $.fn.breadcrumbs = (data) ->
        data2 = 
          { "items": [
            {
              name: "State"
              link: "http://www.google.com" 
            },
            {
              name: "District"
              link: "http://www.cnn.com" 
            },
            {
              name: "School"
              link: "http://www.cnn.com" 
            },
            {
              name: "Grade"
            },
          ]}
        htmlResult = ""
        
        data = data2
        
        output = Mustache.to_html template, data
        this.html output

