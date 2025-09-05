# Audio Files for Tovar Taxi Notifications

This directory contains audio files used for system notifications:

## Required Audio Files:

1. **ping.mp3** - General notification sound (new orders, messages)
2. **success.wav** - Success notifications (order completed, payment received)  
3. **alert.ogg** - Alert/warning notifications (errors, urgent messages)

## Usage:

These files are automatically loaded by the notification system in `/static/js/notifications.js`.

## File Formats:

- MP3: Good compression, widely supported
- WAV: Uncompressed, high quality
- OGG: Open source format, good compression

## Volume:

All sounds are set to 70% volume by default in the notification system.

## Browser Compatibility:

Modern browsers support all three formats. The system will gracefully handle missing files.

## Adding Custom Sounds:

To add new notification sounds:
1. Add the audio file to this directory
2. Update the `sounds` object in `notifications.js`
3. Reference the new sound name in notification calls
