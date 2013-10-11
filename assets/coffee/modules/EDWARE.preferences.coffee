define [
  "jquery"
  "edwareClientStorage"
  "edwareUtil"
], ($, clientStorage, edwareUtil) ->
  
  KEY = 'edware.preferences'
  
  shortTermStorage = new clientStorage.EdwareClientStorage KEY, false
  longTermStorage = new clientStorage.EdwareClientStorage KEY, true
  
  # On logout, clear storage
  $(document).on 'click', '#logout_button', () ->
    shortTermStorage.clear()

  saveAsmtPreference = (asmtType) ->
    savePreferences {"asmtType": asmtType}
    
  getAsmtPreference = () ->
    pref = getPreferences()
    pref = {} if not pref
    pref["asmtType"] || 'Summative'
  
  getSelectedLanguage = () ->
    iso_language = getPreferences true
    lang_id = iso_language.languageId if iso_language
    lang_id || edwareUtil.getUrlParams()['lang'] ||'en'

  saveSelectedLanguage = (lang) ->
    savePreferences {"languageId": lang}, true

  getInterimInfo = () ->
    pref = getPreferences true
    info = pref.interimDisclaimer if pref
    info || false
  
  saveInterimInfo = () ->
    savePreferences {"interimDisclaimerLoaded": true}, true
  
  # Returns storage based whether long term is set to true
  getStorage = (isLongTerm) ->
    isLongTerm = if typeof isLongTerm isnt "undefined" then isLongTerm else false
    if isLongTerm then longTermStorage else shortTermStorage
  
  savePreferences = (data, isLongTerm) ->
    getStorage(isLongTerm).update(data)
  
  getPreferences = (isLongTerm) ->
    JSON.parse(getStorage(isLongTerm).load() || "{}")
    
  saveAsmtPreference:saveAsmtPreference
  getAsmtPreference:getAsmtPreference
  getSelectedLanguage: getSelectedLanguage
  saveSelectedLanguage: saveSelectedLanguage
  getInterimInfo:getInterimInfo
  saveInterimInfo:saveInterimInfo
