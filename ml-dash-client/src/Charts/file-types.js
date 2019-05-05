export const extTypes = [
  [".aac", "AAC audio", "audio/aac"],
  [".abw", "AbiWord document", "application/x-abiword"],
  [".arc", "Archive document (multiple files embedded)", "application/x-freearc"],
  [".avi", "AVI: Audio Video Interleave", "video/x-msvideo"],
  [".azw", "Amazon Kindle eBook format", "application/vnd.amazon.ebook"],
  [".bin", "Any kind of binary data", "application/octet-stream"],
  [".bmp", "Windows OS/2 Bitmap Graphics", "image/bmp"],
  [".bz", "BZip archive", "application/x-bzip"],
  [".bz2", "BZip2 archive", "application/x-bzip2"],
  [".csh", "C-Shell script", "application/x-csh"],
  [".css", "Cascading Style Sheets (CSS)", "text/css"],
  [".csv", "Comma-separated values (CSV)", "text/csv"],
  [".doc", "Microsoft Word", "application/msword"],
  [".docx", "Microsoft Word (OpenXML)", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
  [".eot", "MS Embedded OpenType fonts", "application/vnd.ms-fontobject"],
  [".err", "error output, (generally ASCII or ISO 8859-n)", "text/ansi"],
  [".error", "error output, (generally ASCII or ISO 8859-n)", "text/ansi"],
  [".epub", "Electronic publication (EPUB)", "application/epub+zip"],
  [".gif", "Graphics Interchange Format (GIF)", "image/gif"],
  [".htm", "HyperText Markup Language (HTML)", "text/html"],
  [".html", "HyperText Markup Language (HTML)", "text/html"],
  [".ico", "Icon format", "image/vnd.microsoft.icon"],
  [".ics", "iCalendar format", "text/calendar"],
  [".jar", "Java Archive (JAR)", "application/java-archive"],
  [".jpeg", "JPEG images", "image/jpeg"],
  [".jpg", "JPEG images", "image/jpeg"],
  [".js", "JavaScript", "text/javascript"],
  [".json", "JSON format", "application/json"],
  [".json5", "JSON format", "application/json"],
  [".jsonld", "JSON-LD format", "application/ld+json"],
  [".log", "log output, (generally ASCII or ISO 8859-n)", "text/ansi"],
  [".out", "log output, (generally ASCII or ISO 8859-n)", "text/ansi"],
  [".md", "Markdown", "text/markdown"],
  [".markdown", "Markdown", "text/markdown"],
  [".cm", "Markdown", "text/markdown"],
  [".mid", "Musical Instrument Digital Interface (MIDI)", "audio/midi audio/x-midi"],
  [".midi", "Musical Instrument Digital Interface (MIDI)", "audio/midi audio/x-midi"],
  [".mjs", "JavaScript module", "text/javascript"],
  [".mp3", "MP3 audio", "audio/mpeg"],
  [".mpeg", "MPEG Video", "video/mpeg"],
  [".mpkg", "Apple Installer Package", "application/vnd.apple.installer+xml"],
  [".odp", "OpenDocument presentation document", "application/vnd.oasis.opendocument.presentation"],
  [".ods", "OpenDocument spreadsheet document", "application/vnd.oasis.opendocument.spreadsheet"],
  [".odt", "OpenDocument text document", "application/vnd.oasis.opendocument.text"],
  [".oga", "OGG audio", "audio/ogg"],
  [".ogv", "OGG video", "video/ogg"],
  [".ogx", "OGG", "application/ogg"],
  [".otf", "OpenType font", "font/otf"],
  [".png", "Portable Network Graphics", "image/png"],
  [".pdf", "Adobe Portable Document Format (PDF)", "application/pdf"],
  [".ppt", "Microsoft PowerPoint", "application/vnd.ms-powerpoint"],
  [".pkl", "Python Pickle File", "application/python-pickle"],
  [".pptx", "Microsoft PowerPoint (OpenXML)", "application/vnd.openxmlformats-officedocument.presentationml.presentation"],
  [".rar", "RAR archive", "application/x-rar-compressed"],
  [".rtf", "Rich Text Format (RTF)", "application/rtf"],
  [".sh", "Bourne shell script", "application/x-sh"],
  [".svg", "Scalable Vector Graphics (SVG)", "image/svg+xml"],
  [".swf", "Small web format (SWF) or Adobe Flash document", "application/x-shockwave-flash"],
  [".tar", "Tape Archive (TAR)", "application/x-tar"],
  [".tif", "Tagged Image File Format (TIFF)", "image/tiff"],
  [".tiff", "Tagged Image File Format (TIFF)", "image/tiff"],
  [".ttf", "TrueType Font", "font/ttf"],
  [".txt", "Text, (generally ASCII or ISO 8859-n)", "text/plain"],
  [".text", "Text, (generally ASCII or ISO 8859-n)", "text/plain"],
  [".diff", "git patch file", "text/diff"],
  [".patch", "git patch file", "text/diff"],
  [".vsd", "Microsoft Visio", "application/vnd.visio"],
  [".wav", "Waveform Audio Format", "audio/wav"],
  [".weba", "WEBM audio", "audio/webm"],
  [".webm", "WEBM video", "video/webm"],
  [".webp", "WEBP image", "image/webp"],
  [".woff", "Web Open Font Format (WOFF)", "font/woff"],
  [".woff2", "Web Open Font Format (WOFF)", "font/woff2"],
  [".xhtml", "XHTML", "application/xhtml+xml"],
  [".xls", "Microsoft Excel", "application/vnd.ms-excel"],
  [".xlsx", "Microsoft Excel (OpenXML)", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
  [".xml", "XML", "application/xml if not readable from casual users (RFC 3023, section 3), text/xml if readable from casual users (RFC 3023, section 3)"],
  [".xul", "XUL", "application/vnd.mozilla.xul+xml"],
  [".zip", "ZIP archive", "application/zip"],
  [".3gp", "3GPP audio/video container", "video/3gpp, audio/3gpp if it doesn't contain video"],
  [".3g2", "3GPP2 audio/video container", "video/3gpp2. audio/3gpp2 if it doesn't contain video"],
  [".7z", "7-zip archive", "application/x-7z-compressed"]
].map(([ext, name, mime]) => ({ext, name, mime}));

export const displayTypes = {};
extTypes.forEach(function ({ext, name, mime}) {
  if (mime.match('image'))
    displayTypes[ext] = 'image';
  else if (mime.match('video'))
    displayTypes[ext] = 'video';
  else if (mime.match('ansi')) //todo: not yet displayed differently.
    displayTypes[ext] = 'ansi';
  else if (mime.match('markdown')) //todo: not yet displayed differently.
    displayTypes[ext] = 'markdown';
  else if (mime.match('diff')) //todo: not yet displayed differently.
    displayTypes[ext] = 'text';
  else if (mime.match('pickle'))
    displayTypes[ext] = 'pickle';
  else //todo: what about binary?
    displayTypes[ext] = 'text';
});

export function displayType(name) {
  if (!name) return null;
  let ext = "." + name.split(".").slice(-1)[0];
  return displayTypes[ext]
}
