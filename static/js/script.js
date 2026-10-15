
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("resume-form");
    const previewName = document.getElementById("preview-name");
    const previewContact = document.getElementById("preview-contact");
    const previewLinks = document.getElementById("preview-links");
    const previewSections = document.getElementById("preview-sections");
    const customContainer = document.getElementById("custom-sections");
    const addCustomButton = document.getElementById("add-custom-section");

    if (!form || !previewSections) return;

    const sectionDetails = [
        { id: "summary", title: "Career Objective" },
        { id: "education", title: "Education" },
        { id: "skills", title: "Technical Skills" },
        { id: "projects", title: "Academic Projects" },
        { id: "experience", title: "Experience" },
        { id: "certifications", title: "Certifications" },
        { id: "achievements", title: "Achievements" },
        { id: "languages", title: "Languages" }
    ];

    function getValue(id) {
        return document.getElementById(id)?.value.trim() || "";
    }

    // Accept URLs with or without https:// or http://.
    function normalizeUrl(value) {
        value = value.trim();

        if (!value) return "";

        if (!/^https?:\/\//i.test(value)) {
            value = "https://" + value;
        }

        return value;
    }

    function normalizeProfileInput(inputId) {
        const input = document.getElementById(inputId);

        if (!input) return;

        input.addEventListener("blur", function () {
            if (input.value.trim()) {
                input.value = normalizeUrl(input.value);
                updatePreview();
            }
        });
    }

    // Apply to both LinkedIn and GitHub.
    normalizeProfileInput("linkedin");
    normalizeProfileInput("github");

    function isSectionSelected(id) {
        const checkbox = form.querySelector(
            `input[name="selected_sections"][value="${id}"]`
        );

        return checkbox ? checkbox.checked : true;
    }

    // Show or hide the corresponding form sections.
    function updateFormSections() {
        sectionDetails.forEach(function (section) {
            const card = document.querySelector(
                `.optional-section[data-section="${section.id}"]`
            );

            if (card) {
                card.hidden = !isSectionSelected(section.id);
            }
        });
    }

    function createPreviewSection(title, value) {
        if (!title || !value) return null;

        const section = document.createElement("section");
        section.className = "preview-live-section";

        const heading = document.createElement("h3");
        heading.textContent = title;

        const paragraph = document.createElement("p");
        paragraph.textContent = value;

        section.append(heading, paragraph);

        return section;
    }

    function updatePreview() {
        previewName.textContent = getValue("name") || "Your Name";

        const contactItems = [
            getValue("email"),
            getValue("phone"),
            getValue("address")
        ].filter(Boolean);

        previewContact.textContent =
            contactItems.join(" | ") || "Email | Phone";

        // Show LinkedIn and GitHub in the preview.
        const linkedinValue = getValue("linkedin");
        const githubValue = getValue("github");

        const linkItems = [];

        if (linkedinValue) {
            linkItems.push("LinkedIn: " + linkedinValue);
        }

        if (githubValue) {
            linkItems.push("GitHub: " + githubValue);
        }

        previewLinks.textContent = linkItems.join(" | ");

        previewSections.replaceChildren();

        let visibleSectionCount = 0;

        // Render selected standard sections.
        sectionDetails.forEach(function (section) {
            if (!isSectionSelected(section.id)) return;

            const value = getValue(section.id);

            if (!value) return;

            const previewSection = createPreviewSection(
                section.title,
                value
            );

            if (previewSection) {
                previewSections.appendChild(previewSection);
                visibleSectionCount++;
            }
        });

        // Render custom sections.
        if (customContainer) {
            customContainer
                .querySelectorAll(".custom-section-item")
                .forEach(function (item) {
                    const title = item.querySelector(
                        '[name="custom_title[]"]'
                    )?.value.trim();

                    const content = item.querySelector(
                        '[name="custom_content[]"]'
                    )?.value.trim();

                    if (!title || !content) return;

                    const previewSection = createPreviewSection(
                        title,
                        content
                    );

                    if (previewSection) {
                        previewSections.appendChild(previewSection);
                        visibleSectionCount++;
                    }
                });
        }

        if (visibleSectionCount === 0) {
            const message = document.createElement("p");
            message.className = "empty-preview";
            message.textContent =
                "Your selected resume sections will appear here as you type.";

            previewSections.appendChild(message);
        }
    }

    // Add a new custom section.
    function addCustomSection() {
        if (!customContainer) return;

        const wrapper = document.createElement("div");
        wrapper.className = "custom-section-item";

        const titleGroup = document.createElement("div");
        titleGroup.className = "form-group";

        const titleLabel = document.createElement("label");
        titleLabel.textContent = "Section Title";

        const titleInput = document.createElement("input");
        titleInput.type = "text";
        titleInput.name = "custom_title[]";
        titleInput.placeholder = "e.g. Volunteer Work";
        titleInput.required = true;

        titleGroup.append(titleLabel, titleInput);

        const contentGroup = document.createElement("div");
        contentGroup.className = "form-group";

        const contentLabel = document.createElement("label");
        contentLabel.textContent = "Section Content";

        const contentInput = document.createElement("textarea");
        contentInput.name = "custom_content[]";
        contentInput.rows = 3;
        contentInput.placeholder = "Enter the details...";
        contentInput.required = true;

        contentGroup.append(contentLabel, contentInput);

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "remove-custom-button";
        removeButton.textContent = "Remove Section";

        removeButton.addEventListener("click", function () {
            wrapper.remove();
            updatePreview();
        });

        wrapper.append(
            titleGroup,
            contentGroup,
            removeButton
        );

        customContainer.appendChild(wrapper);
        titleInput.focus();

        updatePreview();
    }

    // Update the live preview when typing.
    form.addEventListener("input", updatePreview);

    // Update preview and optional sections when changed.
    form.addEventListener("change", function (event) {
        if (
            event.target.matches(
                'input[name="selected_sections"]'
            )
        ) {
            updateFormSections();
        }

        updatePreview();
    });

    // Normalize URLs before submitting the form to Flask.
    form.addEventListener("submit", function () {
        ["linkedin", "github"].forEach(function (id) {
            const input = document.getElementById(id);

            if (input && input.value.trim()) {
                input.value = normalizeUrl(input.value);
            }
        });
    });

    if (addCustomButton) {
        addCustomButton.addEventListener("click", addCustomSection);
    }

    // Initialize the page.
    updateFormSections();
    updatePreview();
});
