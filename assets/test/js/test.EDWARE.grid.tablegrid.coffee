#globals ok $ EDWARE test require module equals deepEqual
require ["jquery", "jqGrid", "cs!edwareGrid"], ($, jqGrid, edwareGrid) ->
  module "EDWARE.grid.tablegrid.create",
    setup: ->
      $("body").append "<table id='gridTable'></table>"

    teardown: ->
      $(".ui-jqgrid").remove()

  test "Test create method", ->
    ok edwareGrid.create isnt `undefined`, "EDWARE.grid.tablegrid create method should be defined"
    ok typeof edwareGrid.create is "function", "EDWARE.grid.tablegrid create method should be function"
    columnData = [
      id: "1"
      name: "some long test text"
      amount: "200.00"
      tax: "10.00"
      total: "210.00"
    ,
      id: "2"
      name: "test2"
      amount: "300.00"
      tax: "20.00"
      total: "320.00"
    ,
      id: "3"
      name: "test3"
      amount: "400.00"
      tax: "30.00"
      total: "430.00"
    ,
      id: "4"
      name: "some long test text"
      amount: "200.00"
      tax: "10.00"
      total: "210.00"
    ,
      id: "5"
      name: "test2"
      amount: "300.00"
      tax: "20.00"
      total: "320.00"
    ,
      id: "6"
      name: "test3"
      amount: "400.00"
      tax: "30.00"
      total: "430.00"
    ]
    columnItems = [
      name: "id"
      index: "id"
      width: 150
      align: "center"
      sorttype: "int"
      hidden: true
    ,
      name: "name"
      index: "name"
      width: 150
      style: "ui-ellipsis"
    ,
      name: "amount"
      index: "amount"
      width: 150
      formatter: "number"
      align: "right"
      resizable: false
    ,
      name: "tax"
      index: "tax"
      width: 150
      formatter: "number"
      align: "right"
      resizable: false
    ,
      name: "total"
      index: "total"
      width: 150
      formatter: "number"
      align: "right"
      resizable: false
    ]
    edwareGrid.create "gridTable", columnItems, columnData
    deepEqual $(".ui-jqgrid-htable").length, 1, "Create method should create grid view"
