###
(c) 2014 The Regents of the University of California. All rights reserved,
subject to the license below.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by
applicable law or agreed to in writing, software distributed under the License
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the specific language
governing permissions and limitations under the License.

###

#
# * EDWARE breadcrumbs
# * The module contains EDWARE breadcrumbs plugin and breadcrumbs creation method
#
define [
  'jquery'
  "mustache"
  "edwareUtil"
  "edwareDataProxy"
] , ($, Mustache, edwareUtil, edwareDataProxy) ->

  BREADCRUMBS_TEMPLATE = "<ul>{{#items}}<li><a href='{{link}}' aria-label='breadcrumb {{name}}'>{{name}}</a></li>{{/items}}<ul>"

  class EdwareBreadcrumbs

    constructor: (@container, @contextData, @configs, @displayHome, @labels) ->
      @initialize()
      @bindEvents()

    initialize: ->
      elements = @getCurrentPath()
      output = Mustache.to_html BREADCRUMBS_TEMPLATE,
        items: elements
      $(@container).html output
      # ignore last link
      $('li:last a', @container).attr('tabindex', '-1')

    getCurrentPath: ->
      elements = []
      for element, i in @contextData['items']
        staticElement = @configs['items'][i]
        if staticElement.type isnt element.type
          # make sure the type matches with the type from json file
          continue
        # sets the url link and returns the current query parameters
        currentParams = @setUrlLink currentParams, element, staticElement
        elements.push @formatName element
      if not this.displayHome
        elements.shift()
      if elements.length > 0
        elements[elements.length - 1].link = '#'
      elements

    bindEvents: ->
      items = $('li', @container)
      items.not(':last').addClass('link').hover ()->
        $this = $(this)
        $this.addClass 'active'
        $this.prev().addClass 'preceding'
      , ()->
        $this = $(this)
        $this.removeClass 'active'
        $this.prev().removeClass 'preceding'

    formatName: (element) ->
      type = element.type
      name = element.name
      if type is 'home'
        name = @labels.breadcrumb_home
      else if type is 'grade'
        name = @labels.grade + ' ' + name
      else if type is 'student'
        # Special case for names that end with an 's'
        name += if /s$|S$/.test(name) then "'" else "'s"
        name += " Results"
      element.name = name
      element

    setUrlLink: (currentParams, element, staticElement) ->
      # Appends the current set of query parameters to build breadcrumb link
      # Sets element.link used for individual breadcrumb links
      # currentParams keeps track of existing query parameters for the rest of the breadcrumb trail
      currentParams ?= if edwareUtil.isPublicReport() then 'isPublic=true' else ''
      if element.id
        params = staticElement.queryParam + "=" + element.id
        if currentParams.length is 0
          currentParams = params
        else
          currentParams = currentParams + "&" + params
          currentParams = currentParams.replace /stateCode/, "sid" if edwareUtil.isPublicReport()
        element.link = staticElement.link + "?" + currentParams
      else if staticElement.link
        element.link = staticElement.link
      currentParams

  #
  #    *  EDWARE Breadcrumbs plugin
  #    *  @param data
  #    *  @param configs
  #    *  Example: $("#table1").breadcrumbs(data, configs)
  #
  $.fn.breadcrumbs = (contextData, configs, displayHome, labels) ->
    new EdwareBreadcrumbs(this, contextData, configs, displayHome, labels)

  #
  #    * Creates breadcrumbs widget
  #    * @param containerId - The container id for breadcrumbs
  #    * @param data
  #
  create = (containerId, contextData, configs, displayHome, labels) ->
    $(containerId).breadcrumbs contextData, configs, displayHome, labels

  create: create
  EdwareBreadcrumbs: EdwareBreadcrumbs
