define [
  "jquery"
  "bootstrap"
  "mustache"
  "edwareUtil"
  "edwareLanguageSelector"
  "edwareHelpMenu"
  "text!headerTemplateHtml"
], ($, Bootstrap, Mustache, edwareUtil, edwareLanguageSelector, edwareHelpMenu, headerTemplateHtml) ->

  create = (data, config) ->
    labels = config.labels
    headerTemplate = $(headerTemplateHtml)
    # Add labels
    headerTemplate.find('.text_help').html labels.help
    headerTemplate.find('.text_resources').html labels.resources
    userInfo = data.user_info
    # Add header to the page
    userName = edwareUtil.getUserName userInfo
    if userName
      headerTemplate.find('#user-settings #username').html userName
    header = $("#header").html headerTemplate
    dropdown_menu = header.find '.dropdown-menu'
    # Add language selector
    edwareLanguageSelector.create dropdown_menu, labels
    $('.text_logout').html labels.logout
    createHelp labels
    bindEvents()
    role = edwareUtil.getRole userInfo
    uid = edwareUtil.getUid userInfo

  createHelp = (labels) ->
    @helpMenu = edwareHelpMenu.create '.HelpMenuContainer',
      labels: labels

  bindEvents = ()->
    self = @
    # Popup will close if user clicks popup hide button
    $('#header #help').click ->
      self.helpMenu.show()
    $('#header #log_out_button').click ->
      window.open '/logout', 'iframe_logout'
    $('#header #resources').click ->
      $('#ResourcesModal').modal 'show'
    $('#header .dropdown').mouseleave ->
      $(@).removeClass 'open'

  # The code below is curently not being used.  Waiting to be refactored
  createCommonRegion = ()->
    # create header, breadcrumbs, info bar, action bar
    # process breadcrumbs
    @renderBreadcrumbs(data.context)
    @renderReportInfo()
    @renderReportActionBar()
    @createHeaderAndFooter()

  renderBreadcrumbs: () ->
    $('#breadcrumb').breadcrumbs(@contextData, @config.breadcrumb)

  renderReportInfo: () ->
    edwareReportInfoBar.create '#infoBar',
      reportTitle: @contextData.items[2].name # set school name as the page title from breadcrumb
      reportName: Constants.REPORT_NAME.LOS
      reportInfoText: @config.reportInfo
      labels: @labels
      CSVOptions: @config.CSVOptions

  renderReportActionBar: () ->
    self = this
    @config.colorsData = @cutPointsData
    @config.reportName = Constants.REPORT_NAME.LOS
    asmtTypeDropdown = convertAsmtTypes this.studentsConfig.customViews, this.subjectsData
    @config.asmtTypes = asmtTypeDropdown
    @actionBar ?= edwareReportActionBar.create '#actionBar', @config, (viewName) ->
      # Add dark border color between Math and ELA section to emphasize the division
      $('#gridWrapper').removeClass().addClass(viewName)
      self.updateView viewName

  create: create
