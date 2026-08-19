// Page Generator - Creates pages from templates
class PageGenerator {
    constructor() {
        this.templateCache = new Map();
    }

    // Load template from file
    async loadTemplate(templateName) {
        if (this.templateCache.has(templateName)) {
            return this.templateCache.get(templateName);
        }

        try {
            const response = await fetch(`templates/${templateName}.html`);
            if (!response.ok) {
                throw new Error(`Failed to load template: ${templateName}`);
            }
            const template = await response.text();
            this.templateCache.set(templateName, template);
            return template;
        } catch (error) {
            console.error(`Error loading template ${templateName}:`, error);
            return '';
        }
    }

    // Replace placeholders in template
    replacePlaceholders(template, placeholders) {
        let result = template;
        for (const [key, value] of Object.entries(placeholders)) {
            const regex = new RegExp(`{{${key}}}`, 'g');
            result = result.replace(regex, value);
        }
        return result;
    }

    // Generate page from template
    async generatePage(templateName, placeholders = {}) {
        const template = await this.loadTemplate(templateName);
        if (!template) {
            throw new Error(`Template ${templateName} not found`);
        }
        return this.replacePlaceholders(template, placeholders);
    }

    // Create a new page file
    async createPage(templateName, outputPath, placeholders = {}) {
        try {
            const pageContent = await this.generatePage(templateName, placeholders);

            // In a real application, you would write to file system
            // For now, we'll return the content
            return {
                success: true,
                content: pageContent,
                path: outputPath
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Create global instance
window.pageGenerator = new PageGenerator();

// Helper function to create pages
window.createPage = async (templateName, placeholders = {}) => {
    return await window.pageGenerator.generatePage(templateName, placeholders);
};
