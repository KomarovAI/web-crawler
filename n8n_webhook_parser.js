// 🔥 N8N WEBHOOK PARSER v2
// Парсит webhook payload и валидирует depth_level (NOT max_pages!)

// Получи данные из Webhook
const payload = $input.item.json.body || {};

// URL валидация
const url = String(payload.url || 'https://callmedley.com').trim();
if (!url.startsWith('http://') && !url.startsWith('https://')) {
  throw new Error(`Invalid URL: ${url}. Must start with http:// or https://`);
}

// ⚡ НОВОЕ: depth_level вместо max_pages
const depthLevelStr = String(payload.depth_level || '2').trim();
const depthLevel = parseInt(depthLevelStr, 10);

if (isNaN(depthLevel) || depthLevel < 1 || depthLevel > 4) {
  throw new Error(
    `depth_level must be 1-4, got ${depthLevelStr}.\n` +
    `Levels:\n` +
    `  1 = Start page only (fast)\n` +
    `  2 = Start + direct children (recommended)\n` +
    `  3 = Start + 2 levels deep\n` +
    `  4 = Very deep crawl (slow, be careful!)`
  );
}

// Output directory (optional, with sanitization)
const outputDir = String(payload.output_dir || 'site_archive').trim()
  .replace(/[^a-zA-Z0-9_-]/g, ''); // Sanitize

if (outputDir.length === 0) {
  throw new Error('output_dir is empty after sanitization');
}

// Get level description for logging
const levelDescriptions = {
  1: 'Start page only (fastest)',
  2: 'Start + direct child pages (recommended)',
  3: 'Start + children + grandchildren (deeper)',
  4: 'Very deep crawl (slow, be careful!)'
};

const levelDescription = levelDescriptions[depthLevel] || 'Unknown';

// ✅ Return validated payload
// resumeUrl генерируется автоматически n8n и передаётся в GitHub ноду через {{ $resumeWebhookUrl }}
return {
  url,
  depth_level: depthLevel,
  depth_level_description: levelDescription,
  output_dir: outputDir,
  // НЕ добавляй resumeUrl сюда — передавай через {{ $resumeWebhookUrl }} в GitHub ноде
};
