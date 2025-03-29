/**
 * Markdown and LaTeX Renderer
 * A utility for rendering Markdown and LaTeX content in HTML elements
 */

// Function to render LaTeX in an element
function renderMath(element) {
  // Ensure the KaTeX auto-render function is available
  if (typeof renderMathInElement === 'function') {
    renderMathInElement(element, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false },
        { left: '\\[', right: '\\]', display: true },
      ],
      throwOnError: false,
    });
  } else {
    // If KaTeX isn't loaded yet, try again in a moment
    setTimeout(() => renderMath(element), 100);
  }
}

// Configure marked.js to handle LaTeX properly
function configureMarked() {
  if (typeof marked !== 'undefined') {
    marked.use({
      mangle: false,
      headerIds: false,
      breaks: true,
    });
  }
}

// Function to render markdown and LaTeX in an element
function renderMarkdownAndLatex(element, text) {
  if (!element) return;
  
  // Configure marked if needed
  configureMarked();
  
  // Render markdown
  element.innerHTML = marked.parse(text);
  
  // Render LaTeX after markdown is processed
  renderMath(element);
}

// Function to render only LaTeX in an element (no Markdown processing)
function renderLatexOnly(element) {
  if (!element) return;
  
  // Just render LaTeX equations in the existing content
  renderMath(element);
}
