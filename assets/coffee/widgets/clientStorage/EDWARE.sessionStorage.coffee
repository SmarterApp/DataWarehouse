###
# Edware Session Storage #

This module provides client side session storage.
###
define [
  "jquery"
  "edwareUtil"
], ($, edwareUtil) ->

  clearAll = () ->
    ### Clears all session storage. ###
    sessionStorage.clear()

  loadKeyPrefix = () ->
    ### Loads user information and use user guid as key prefix. ###
    guid = ''
    $.getJSON("/services/userinfo").done (data) ->
      guid = edwareUtil.getGuid data.user_info
    guid
    
  PREFIX = loadKeyPrefix()

  ### Edware session storage. ###
  class EdwareSessionStorage

    constructor: (key) ->
      ### Constructor with storage key as parameter. ###
      this.key = PREFIX + key

    load: () ->
      ### Loads data from session storage###
      sessionStorage.getItem(this.key)

    save: (data) ->
      ###
      Saves data into session storage.
      Data must be able to convert to a JSON string in order to be put into session storage.
      ###
      sessionStorage.setItem(this.key, JSON.stringify(data))

    clear: () ->
      ### Clear data ###
      sessionStorage.removeItem(this.key)

  ###
  Filter Storage
  ###
  filterStorage: new EdwareSessionStorage('edware.filter.params')
  i18nStorage: new EdwareSessionStorage('edware.i18n.iso.language')
  clearAll: clearAll
