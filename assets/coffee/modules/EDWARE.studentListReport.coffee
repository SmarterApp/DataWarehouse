require [
  "edwareStudentList"
  "edwareFilter"
  "edwareDataProxy"
  "edwareConstants"
  "edwarePreferences"
], (edwareStudentList, edwareFilter, edwareDataProxy, Constants,
  edwarePreferences) ->

  reportName = Constants.REPORT_JSON_NAME.LOS

  edwareDataProxy.getDataForReport(reportName).done (config) ->
    studentGrid = new edwareStudentList.StudentGrid(config)
    # Add filter to the page
    edwareDataProxy.getDataForFilter().done (configs)->
      filter = $('#losFilter').edwareFilter '.filterItem', configs, (param)->
        param = mergeWithPreference(param)
        studentGrid.reload(param)
      filter.loadReport()
      filter.update {}

  mergeWithPreference = (params)->
    asmtYear = edwarePreferences.getAsmtYearPreference()
    params['asmtYear'] = asmtYear if asmtYear
    asmt = edwarePreferences.getAsmtPreference()
    params.asmtType = asmt?.asmtType
    params
