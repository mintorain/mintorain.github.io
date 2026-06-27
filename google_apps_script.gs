var SPREADSHEET_ID = "YOUR_SPREADSHEET_ID";
var SHEET_NAME = "leads";
var DEFAULT_DEVELOPER = "이신우";
var DUPLICATE_WINDOW_MS = 5 * 1000;

function doGet() {
  return ContentService
    .createTextOutput("OK")
    .setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  var params = e && e.parameter ? e.parameter : {};

  var name = sanitizeText(params.name);
  var phone = normalizePhone(params.phone);
  var developer = sanitizeText(params.developer) || DEFAULT_DEVELOPER;
  var inquiryType = sanitizeText(params.inquiryType);
  var unitType = sanitizeText(params.unitType);
  var visitDateTime = sanitizeText(params.visitDateTime);
  var consent = sanitizeText(params.consent);
  var pageUrl = sanitizeText(params.pageUrl);
  var device = sanitizeText(params.device);
  var createdAt = sanitizeText(params.createdAt) || new Date().toISOString();
  var requestId = sanitizeText(params.requestId);
  var leadSource = sanitizeText(params.leadSource);
  var note = sanitizeText(params.note);

  if (!name || !phone) {
    return jsonResponse({
      ok: false,
      message: "Missing required fields"
    });
  }

  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);

  if (!sheet) {
    return jsonResponse({
      ok: false,
      message: "Sheet not found"
    });
  }

  if (isDuplicateLead(sheet, requestId, phone, createdAt)) {
    return jsonResponse({
      ok: true,
      duplicate: true,
      message: "Duplicate ignored"
    });
  }

  sheet.appendRow([
    createdAt,
    name,
    phone,
    developer,
    inquiryType,
    unitType,
    visitDateTime,
    consent,
    pageUrl,
    device,
    note,
    requestId,
    leadSource
  ]);

  return jsonResponse({
    ok: true,
    message: "Saved"
  });
}

function sanitizeText(value) {
  return String(value || "").trim();
}

function normalizePhone(value) {
  return String(value || "").replace(/[^0-9]/g, "");
}

function jsonResponse(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function isDuplicateLead(sheet, requestId, phone, createdAt) {
  var lastRow = sheet.getLastRow();

  if (lastRow < 2) {
    return false;
  }

  var startRow = Math.max(2, lastRow - 20);
  var numRows = lastRow - startRow + 1;
  var values = sheet.getRange(startRow, 1, numRows, 13).getValues();
  var createdTime = Date.parse(createdAt);

  for (var i = values.length - 1; i >= 0; i--) {
    var row = values[i];
    var rowCreatedAt = String(row[0] || "");
    var rowPhone = normalizePhone(row[2]);
    var rowRequestId = String(row[11] || "");

    if (requestId && rowRequestId && requestId === rowRequestId) {
      return true;
    }

    if (rowPhone === phone && createdTime && Date.parse(rowCreatedAt)) {
      if (Math.abs(createdTime - Date.parse(rowCreatedAt)) < DUPLICATE_WINDOW_MS) {
        return true;
      }
    }
  }

  return false;
}

function setupSheetHeader() {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = SpreadsheetApp.openById(SPREADSHEET_ID).insertSheet(SHEET_NAME);
  }

  var headers = [[
    "접수일시",
    "이름",
    "연락처",
    "개발자정보",
    "문의유형",
    "관심평형",
    "방문희망일시",
    "개인정보동의",
    "유입페이지",
    "사용자기기",
    "비고",
    "요청ID",
    "유입소스"
  ]];

  sheet.getRange(1, 1, 1, headers[0].length).setValues(headers);
  sheet.setFrozenRows(1);
}
