// Main JavaScript file for KapiyuGuide
document.addEventListener('DOMContentLoaded', function() {
    // Detect scroll for potential sticky header adjustments
    window.addEventListener('scroll', function() {
        const scrollPosition = window.scrollY;
        const header = document.querySelector('header');
        
        if (scrollPosition > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    
    // Responsive image loading
    const handleResponsiveImages = () => {
        const windowWidth = window.innerWidth;
        const images = document.querySelectorAll('img[data-src]');
        
        images.forEach(img => {
            // Load appropriate image size based on screen width
            if (windowWidth < 640) {
                img.src = img.getAttribute('data-src-sm');
            } else if (windowWidth < 1024) {
                img.src = img.getAttribute('data-src-md');
            } else {
                img.src = img.getAttribute('data-src');
            }
        });
    };
    
    // Initial call and resize listener
    handleResponsiveImages();
    window.addEventListener('resize', handleResponsiveImages);
    
    // Form validation is handled in the index.html file
});