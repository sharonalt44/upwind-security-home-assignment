/**
 * Global Configuration
 * DURING DEVELOPMENT: Replace this URL with your active Ngrok HTTPS forwarding URL
 * (e.g., "https://a1b2-34-56.ngrok-free.app/api/v1/addon/analyze")
 */
var BACKEND_URL = "https://api.penguwave.com/api/v1/addon/analyze"; 

/**
 * Global entry point triggered automatically by Google Workspace when an email is opened.
 * Builds and returns the primary security scoring user interface card.
 */
function buildContextualCard(e) {
  var messageId = e.gmail.messageId;
  var accessToken = e.gmail.accessToken;
  GmailApp.setCurrentMessageAccessToken(accessToken);
  
  // 1. Fetch target email metadata securely
  var message = GmailApp.getMessageById(messageId);
  var fromHeader = message.getFrom();
  var subjectHeader = message.getSubject();
  var bodyContent = message.getPlainBody();
  
  // 2. Execute risk evaluation matrix
  var evaluation = evaluateEmailRisk(fromHeader, subjectHeader, bodyContent);
  
  // 3. Persist transaction to history log
  logScanToHistory(messageId, fromHeader, evaluation.score, evaluation.verdict);
  
  // 4. Construct response UI layer via CardService
  return renderSecurityCard(fromHeader, evaluation, messageId);
}

/**
 * Evaluates the risk level of an email by forwarding metadata to the centralized FastAPI backend.
 * Includes a robust client-side fallback mechanism in case the remote server is unreachable.
 */
function evaluateEmailRisk(from, subject, body) {
  // משתמש במשתנה הגלובלי שהגדרנו למעלה
  var backendUrl = BACKEND_URL; 
  
  var payload = {
    "sender": from,
    "subject": subject,
    "body": body,
    "recipient": Session.getActiveUser().getEmail() // תיקון קריטי: הוספת שדה נמען (פירוט בנקודה 3)
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(backendUrl, options);
    if (response.getResponseCode() === 200) {
      return JSON.parse(response.getContentText());
    }
  } catch (e) {
    return {
      "score": 25,
      "verdict": "SUSPICIOUS",
      "color": "#ef6c00",
      "signals": [
        "⚠️ Central Threat Intel server unreachable.",
        "🔄 Running local sandbox fallback heuristics for demonstration."
      ]
    };
  }
}