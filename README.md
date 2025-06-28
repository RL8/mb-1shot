# Mobile Vue App

A Vue 3 application designed exclusively for mobile browsers with no desktop accommodations.

## Features

### 🎯 Mobile-First Design
- Optimized exclusively for mobile viewport (no desktop responsiveness)
- Touch-friendly interface with proper tap targets (minimum 44px)
- Mobile-specific gestures and interactions

### 📱 Mobile Optimizations
- **Viewport Configuration**: Prevents zooming and ensures proper mobile rendering
- **Safe Area Support**: Handles iPhone notches and Android navigation bars
- **Touch Optimizations**: Eliminates text selection and callouts where inappropriate
- **Performance**: Fast loading with Vite bundler

### 🎨 UI Components
- **Fixed Header**: Blur backdrop with mobile navigation
- **Touch Buttons**: Large, touch-friendly buttons with visual feedback
- **Slide-out Menu**: Right-side navigation drawer
- **Toast Notifications**: Mobile-style popup messages
- **Card Layout**: Clean, modern card-based interface

### 🔧 Technical Stack
- **Vue 3**: Composition API with reactive features
- **Vite**: Fast development and build tool
- **CSS Variables**: Consistent theming system
- **ES Modules**: Modern JavaScript features

## Development

### Start Development Server
```bash
npm run dev
```
Access at: http://localhost:3001/

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Mobile Testing

### On Your Device
1. Ensure your computer and phone are on the same WiFi network
2. Open `http://192.168.1.204:3001/` on your mobile browser
3. Test touch interactions and responsiveness

### Browser DevTools
1. Open Chrome DevTools
2. Toggle device simulation (F12 → Mobile icon)
3. Select a mobile device preset
4. Test in portrait and landscape modes

## App Structure

```
src/
├── App.vue          # Main app component with mobile layout
├── main.js          # Vue app initialization
└── style.css        # Mobile-first CSS styles

public/              # Static assets
index.html           # Main HTML with mobile meta tags
package.json         # Dependencies and scripts
vite.config.js       # Vite configuration
```

## Key Mobile Features

### Navigation
- **Header Menu**: Tap hamburger (☰) to open side navigation
- **Touch Feedback**: Visual feedback on all interactive elements
- **Smooth Animations**: Native-feeling transitions

### Interactions
- **Tap Actions**: All buttons respond to touch with scale animation
- **Feature Cards**: Tap any feature card to see feedback
- **Menu Items**: Navigate through app sections

### Notifications
- **Toast Messages**: Appear at bottom with auto-dismiss
- **Action Feedback**: Confirm user interactions

## Customization

### Colors (CSS Variables)
```css
--primary-color: #007AFF;      /* iOS blue */
--secondary-color: #34C759;    /* iOS green */
--background-color: #f5f5f5;   /* Light gray */
--card-background: #ffffff;    /* White cards */
```

### Typography
- System fonts optimized for mobile readability
- Touch-appropriate font sizes (minimum 16px)
- Proper line heights for mobile reading

## Browser Support

Optimized for modern mobile browsers:
- iOS Safari 12+
- Chrome Mobile 70+
- Firefox Mobile 68+
- Samsung Internet 10+

## Performance

- **First Load**: ~100ms (Vite HMR)
- **Bundle Size**: Minimal (Vue 3 + custom CSS only)
- **Runtime**: Optimized for 60fps animations on mobile

---

**Note**: This app intentionally provides no desktop support or responsive design for larger screens, focusing exclusively on mobile user experience. 