# Site Improvements: UI Enhancements and Embedding Configuration

**Feature**: Site UI Improvements and Embedding Configuration  
**Branch**: `004-site-improvements`  
**Date**: 2025-01-27  
**Status**: ✅ Complete

## Overview

This feature enhances the user experience with professional branding, improved chat formatting, and a more organized admin interface. It also adds the ability to select between different embedding providers without requiring a backend restart.

## Features Implemented

### 1. Branded Site Experience

**User Story**: Users visiting the site see a professional branded experience with logo and favicon.

**Implementation**:
- Added SVG logo (`frontend/public/logo.svg`) displayed in the application header
- Added SVG favicon (`frontend/public/favicon.svg`) for browser tabs and bookmarks
- Created `Header` component with logo and navigation links
- Integrated header into root layout for consistent branding across all pages

**Files Modified**:
- `frontend/app/layout.tsx` - Added favicon metadata and Header component
- `frontend/components/header.tsx` - New header component with logo and navigation
- `frontend/public/logo.svg` - Logo asset
- `frontend/public/favicon.svg` - Favicon asset

### 2. Markdown Rendering in Chat

**User Story**: Users receive chat responses that are properly formatted with markdown support.

**Implementation**:
- Integrated `react-markdown` with `rehype-highlight` for syntax highlighting
- Added `rehype-sanitize` for XSS protection
- Created `MarkdownRenderer` component with custom styling for:
  - Code blocks with syntax highlighting (language-specific colors)
  - Inline code with monospace styling
  - Headings (h1, h2, h3) with appropriate sizing
  - Lists (ordered and unordered) with proper indentation
  - Links with hover effects and security attributes
  - Paragraphs with proper spacing

**Files Modified**:
- `frontend/components/chat/markdown-renderer.tsx` - New markdown rendering component
- `frontend/components/chat/message-list.tsx` - Updated to use MarkdownRenderer for answer messages
- `frontend/package.json` - Added dependencies: `react-markdown`, `rehype-highlight`, `rehype-sanitize`, `highlight.js`

**Styling**:
- Uses Tailwind CSS utilities for consistent styling
- Code blocks use `highlight.js` GitHub theme
- Responsive design with proper overflow handling for long code blocks

### 3. Organized Admin Interface

**User Story**: Administrators manage content through a well-organized admin interface with categorized sections.

**Implementation**:
- Reorganized admin page into three tabs using `shadcn/ui` Tabs component:
  - **Content Management**: Document upload and management
  - **Settings**: Embedding provider configuration
  - **System Status**: Ingestion status and controls
- Created separate tab components for better code organization:
  - `ContentManagementTab` - Upload form and document list
  - `SettingsTab` - Embedding provider selector
  - `SystemStatusTab` - Ingestion status component
- Used `shadcn/ui` Card components for visual grouping within tabs

**Files Modified**:
- `frontend/app/admin/page.tsx` - Reorganized with Tabs component
- `frontend/components/admin/content-management-tab.tsx` - New tab component
- `frontend/components/admin/settings-tab.tsx` - New tab component
- `frontend/components/admin/system-status-tab.tsx` - New tab component
- `frontend/components/ui/tabs.tsx` - shadcn/ui Tabs component
- `frontend/components/ui/card.tsx` - shadcn/ui Card component

**Improvements**:
- Better visual hierarchy with card-based layout
- Easier navigation with tabbed interface
- Improved state management with forced remount on tab switch to ensure fresh data

### 4. Embedding Provider Selection

**User Story**: Administrators can select between different embedding providers from the admin interface.

**Implementation**:

**Backend**:
- Added `update_embedding_provider()` function in `config.py` to update environment variable
- Created API endpoints:
  - `GET /admin/config/embedding-provider` - Get current provider and available options
  - `PUT /admin/config/embedding-provider` - Update provider preference
- Provider changes persist to `.env` file and take effect on next ingestion (no restart required)
- Supports two providers:
  - **OpenAI**: `text-embedding-3-small` (1536 dimensions) - requires API key
  - **Local**: `sentence-transformers` with `all-MiniLM-L6-v2` (384 dimensions) - no API key required

**Frontend**:
- Created `EmbeddingProviderSelector` component with dropdown selection
- Integrated into Settings tab of admin page
- Displays current provider and available options with descriptions
- Shows success/error messages via toast notifications
- Handles loading and error states gracefully

**Files Modified**:
- `backend/src/config.py` - Added `update_embedding_provider()` function
- `backend/src/api/models.py` - Added `ConfigResponse`, `UpdateConfigRequest`, `ProviderOption` models
- `backend/src/api/routes/admin.py` - Added embedding provider config endpoints
- `frontend/components/admin/embedding-provider-selector.tsx` - New component
- `frontend/lib/api/admin.ts` - Added `getEmbeddingProvider()` and `updateEmbeddingProvider()` functions

**Configuration**:
- Provider preference stored in `EMBEDDING_PROVIDER` environment variable
- Values: `"openai"`, `"local"`, or `""` (empty string for auto-detect)
- Auto-detect logic: Uses OpenAI if API key is available, otherwise falls back to local

### 5. Layout Improvements

**Additional Improvements**:
- Adjusted chat interface height to fit within full page without scrolling
- Input box always visible at bottom of chat screen
- Improved flexbox layout for proper space distribution
- Header component with consistent navigation across pages

**Files Modified**:
- `frontend/app/layout.tsx` - Full-height layout with flexbox
- `frontend/app/page.tsx` - Adjusted container height
- `frontend/components/chat/chat-interface.tsx` - Height adjustments for proper scrolling

### 6. Delete Functionality Enhancements

**Improvements**:
- Enhanced delete endpoint with URL decoding for special characters
- Added post-deletion verification to ensure complete removal
- Improved error handling and logging
- Optimistic UI updates for immediate feedback
- Forced component remount on tab switch to ensure fresh data

**Files Modified**:
- `backend/src/api/routes/admin.py` - Enhanced `delete_document` endpoint
- `frontend/components/admin/document-list.tsx` - Optimistic updates and error handling
- `frontend/app/admin/page.tsx` - Added key prop for forced remount

## Technical Details

### Dependencies Added

**Frontend**:
```json
{
  "react-markdown": "^9.0.0",
  "rehype-highlight": "^7.0.0",
  "rehype-sanitize": "^6.0.0",
  "highlight.js": "^11.9.0",
  "@radix-ui/react-tabs": "^1.0.0"
}
```

**Backend**:
- No new dependencies (uses existing sentence-transformers support)

### API Endpoints

#### GET /admin/config/embedding-provider

Get current embedding provider configuration.

**Response**:
```json
{
  "embedding_provider": "openai",
  "embedding_model": "text-embedding-3-small",
  "available_providers": [
    {
      "value": "openai",
      "label": "OpenAI (text-embedding-3-small)",
      "description": "Uses OpenAI API for embeddings. Requires API key."
    },
    {
      "value": "local",
      "label": "Local (all-MiniLM-L6-v2)",
      "description": "Uses a local sentence-transformers model. No API key required."
    }
  ]
}
```

#### PUT /admin/config/embedding-provider

Update embedding provider preference.

**Request**:
```json
{
  "embedding_provider": "openai"
}
```

**Response**: Same as GET endpoint with updated values.

### Environment Variables

**New Variable**:
- `EMBEDDING_PROVIDER`: Embedding provider preference (`"openai"`, `"local"`, or `""` for auto-detect)

**Updated Behavior**:
- Provider selection persists to `backend/.env` file
- Changes take effect on next ingestion operation (no restart required)
- Backend reads from environment variable on each embedding operation

## User Guide

### Using the Admin Interface

1. **Navigate to Admin Page**: Go to http://localhost:3000/admin

2. **Content Management Tab**:
   - Upload documents using the upload form
   - View and manage all ingested documents
   - Filter by source type (All, Website, Files)
   - Delete documents (removes from database and pgvector)

3. **Settings Tab**:
   - Select embedding provider from dropdown:
     - **OpenAI**: Uses `text-embedding-3-small` (requires API key)
     - **Local**: Uses `all-MiniLM-L6-v2` (no API key required)
   - Changes are saved immediately and take effect on next ingestion

4. **System Status Tab**:
   - Monitor ingestion status
   - Trigger new ingestion operations
   - View ingestion progress and results

### Switching Embedding Providers

1. Navigate to Admin → Settings tab
2. Select desired provider from dropdown
3. Wait for success confirmation
4. Trigger a new ingestion operation
5. The new provider will be used for that ingestion

**Note**: Existing embeddings in the database are not affected. Only new chunks from future ingestions will use the selected provider.

## Architecture Decisions

### Markdown Rendering

**Decision**: Use `react-markdown` with `rehype-highlight` and `rehype-sanitize`

**Rationale**:
- `react-markdown` is the most popular and well-maintained markdown renderer for React
- `rehype-highlight` provides syntax highlighting with minimal configuration
- `rehype-sanitize` prevents XSS attacks by sanitizing HTML output
- Both plugins integrate seamlessly with `react-markdown`

**Alternatives Considered**:
- `marked` + `DOMPurify`: More manual setup, less React-friendly
- `markdown-to-jsx`: Less feature-rich, no built-in plugin system

### Admin Page Organization

**Decision**: Use `shadcn/ui` Tabs component for categorization

**Rationale**:
- Tabs provide clear visual separation of functionality
- Consistent with modern admin interfaces
- `shadcn/ui` components are already in use, maintaining design consistency
- Easy to extend with additional tabs in the future

**Alternatives Considered**:
- Accordion: Less suitable for persistent navigation
- Sidebar navigation: More complex, requires more space
- Single page with sections: Less organized, harder to navigate

### Embedding Provider Persistence

**Decision**: Store in environment variable, update via API

**Rationale**:
- Environment variables are the standard way to configure backend services
- Changes persist across restarts
- No need for additional database tables or configuration files
- API endpoint allows frontend to update without direct file access

**Alternatives Considered**:
- Database table: Overkill for a single configuration value
- Configuration file (JSON/YAML): Less standard, harder to integrate with existing `.env` setup
- In-memory only: Would not persist across restarts

## Testing

### Manual Testing Checklist

- [x] Logo displays in header on all pages
- [x] Favicon appears in browser tab
- [x] Markdown formatting renders correctly (headings, lists, code, links)
- [x] Code blocks have syntax highlighting
- [x] Admin page has three tabs (Content Management, Settings, System Status)
- [x] Embedding provider selector displays current provider
- [x] Embedding provider can be switched and persists
- [x] Provider change takes effect on next ingestion
- [x] Chat interface fits within full page without scrolling
- [x] Document deletion works correctly and removes from database

### Automated Tests (Pending)

- E2E tests for logo and favicon display
- Unit tests for markdown rendering component
- Integration tests for embedding provider API
- E2E tests for admin page tab navigation
- E2E tests for embedding provider switching workflow

## Performance Considerations

- Markdown rendering uses `react-markdown` which is optimized for React
- Syntax highlighting is applied only to code blocks (not inline code)
- Sanitization is performed efficiently via `rehype-sanitize`
- Embedding provider selection has no performance impact (only affects new ingestions)

## Security Considerations

- Markdown content is sanitized via `rehype-sanitize` to prevent XSS attacks
- Embedding provider API endpoint validates input values
- Environment variable updates are logged for audit purposes
- No user input is directly written to environment files without validation

## Future Enhancements

- [ ] Per-user embedding provider preferences (if multi-user support is added)
- [ ] Embedding provider performance metrics and recommendations
- [ ] Additional markdown features (tables, footnotes) if needed
- [ ] Custom logo/favicon upload in admin interface
- [ ] Markdown preview in document upload form
- [ ] Embedding provider auto-selection based on content type or size

## Related Documentation

- [Feature Specification](./specs/004-site-improvements/spec.md) - Original requirements
- [API Contract](./specs/004-site-improvements/contracts/api.yaml) - OpenAPI specification
- [Implementation Plan](./specs/004-site-improvements/plan.md) - Technical implementation plan
- [Research Decisions](./specs/004-site-improvements/research.md) - Technology choices and rationale

## Changelog

### 2025-01-27
- Initial implementation
- Added logo and favicon
- Implemented markdown rendering with syntax highlighting
- Reorganized admin page with tabs
- Added embedding provider selection
- Improved chat layout and delete functionality

