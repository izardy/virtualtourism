# Tasks: Admin Panel

- [x] 1. Access control
  - [x] 1.1 Create `admin` blueprint with `login_required` + `admin_required` on all routes
  - [x] 1.2 Add CSRF protection (Flask-WTF `CSRFProtect`)
  - _Requirements: 1, 5_

- [x] 2. Upload service
  - [x] 2.1 Implement `save_upload` with extension allowlist, size limits and unique sanitized names
  - [x] 2.2 Implement `delete_upload` with reference check
  - _Requirements: 3, 5_

- [x] 3. Destination management
  - [x] 3.1 Create, update and delete handlers with validation
  - [x] 3.2 Handle model, thumbnail and hero image uploads and replacement
  - _Requirements: 2, 3_

- [x] 4. Hotspot management
  - [x] 4.1 Create, update and delete handlers with numeric validation
  - [x] 4.2 Handle hotspot image and audio uploads
  - _Requirements: 3, 4_

- [x] 5. Admin UI (`admin.html`)
  - [x] 5.1 Dashboard with destination list and forms
  - [x] 5.2 Hotspot table and forms per destination
  - [x] 5.3 Flash messages, delete confirmations
  - [ ] 5.4 (Optional) 3D coordinate picker using `ModelLoader`
  - _Requirements: 2, 4_

- [x] 6. Verification
  - [x] 6.1 Non-admin gets 403; anonymous is redirected
  - [x] 6.2 Reject bad extension and oversize file
  - [ ] 6.3 End to end: new destination with GLB and hotspot appears on explore and in the viewer
  - _Requirements: 1-5_

- [ ] 7. Upload a real GLB through the admin panel and open it in the viewer (end-to-end)
- [ ] 8. (Optional) 3D coordinate picker using the viewer's raycasting
