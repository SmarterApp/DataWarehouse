define [
  "jquery"
  "edwareClientStorage"
  "edwareUtil"
  "edwareConstants"
], ($, clientStorage, edwareUtil, Constants) ->

  KEY = 'edware.preferences'

  shortTermStorage = new clientStorage.EdwareClientStorage KEY, false
  longTermStorage = new clientStorage.EdwareClientStorage KEY, true

  # On logout, clear storage
  $(document).on 'click', '#logout_button', () ->
    shortTermStorage.clear()

  saveAsmtYearPreference = (year) ->
    savePreferences {"asmtYear": year}

  getAsmtYearPreference = () ->
    pref = getPreferences() || {}
    pref["asmtYear"]

  saveEffectiveDate = (effectiveDate) ->
      savePreferences {"effectiveDate": effectiveDate}

  getEffectiveDate = () ->
      pref = getPreferences() || {}
      pref["effectiveDate"]

  saveAsmtType = (asmtType) ->
    savePreferences {"asmtType": asmtType}

  getAsmtType = () ->
    pref = getPreferences() || {}
    pref["asmtType"]

  saveAsmtPreference = (asmt) ->
    saveAsmtForISR asmt
    savePreferences {"asmt" : asmt}

  saveAsmtForISR = (asmt) ->
    saveEffectiveDate asmt.effectiveDate
    saveAsmtType asmt.asmtType

  getAsmtForISR = () ->
    [getEffectiveDate(), getAsmtType()]

  getAsmtPreference = () ->
    pref = getPreferences()
    pref = {} if not pref
    pref["asmt"]

  clearAsmtPreference = ->
    saveAsmtPreference {}

  saveSubjectPreference = (asmtSubject) ->
    savePreferences {"asmtSubject": asmtSubject}

  getSubjectPreference = () ->
    pref = getPreferences()
    pref = {} if not pref
    pref["asmtSubject"] || []

  getSelectedLanguage = () ->
    iso_language = getPreferences true
    lang_id = iso_language.languageId if iso_language
    lang_id || edwareUtil.getUrlParams()['lang'] ||'en'

  saveSelectedLanguage = (lang) ->
    savePreferences {"languageId": lang}, true

  getInterimInfo = () ->
    pref = getPreferences true
    info = pref.interimDisclaimerLoaded if pref
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
  clearAsmtPreference: clearAsmtPreference
  saveSubjectPreference:saveSubjectPreference
  getSubjectPreference:getSubjectPreference
  getSelectedLanguage: getSelectedLanguage
  saveSelectedLanguage: saveSelectedLanguage
  getInterimInfo:getInterimInfo
  saveInterimInfo:saveInterimInfo
  saveAsmtYearPreference: saveAsmtYearPreference
  getAsmtYearPreference: getAsmtYearPreference
  saveEffectiveDate: saveEffectiveDate
  getEffectiveDate: getEffectiveDate
  saveAsmtType: saveAsmtType
  getAsmtType: getAsmtType
  saveAsmtForISR: saveAsmtForISR
  getAsmtForISR: getAsmtForISR
