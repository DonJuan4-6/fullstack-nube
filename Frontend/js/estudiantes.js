(() => {
    const form = document.getElementById("student-form");
    const modal = document.getElementById("student-modal");
    const tbody = document.getElementById("students-table");
    const search = document.getElementById("student-search");

    if (!form) return;

    const open = () => {
        modal.classList.add("show");
    };

    const close = () => {
        modal.classList.remove("show");
        form.reset();

        document.getElementById("student-id").value = "";
        document.getElementById("student-modal-title").textContent = "Registrar estudiante";
    };

    document.getElementById("open-student-modal").addEventListener("click", open);

    document.querySelectorAll("[data-close-modal]").forEach(button => {
        button.addEventListener("click", close);
    });

    modal.addEventListener("click", event => {
        if (event.target === modal) {
            close();
        }
    });

    async function render() {
        const students = await GS.store.getStudents();
        const term = search.value.toLowerCase();

        const filtered = students.filter(student => [
            student.nombre,
            student.documento,
            student.correo
        ].join(" ").toLowerCase().includes(term));

        document.getElementById("student-count").textContent =
            `${filtered.length} estudiante(s)`;

        tbody.innerHTML = filtered.length
            ? filtered.map(student => `
                <tr>
                    <td>
                        <span class="student-name">
                            ${GS.esc(student.nombre)}
                        </span>
                    </td>
                    <td>${GS.esc(student.documento)}</td>
                    <td>${GS.esc(student.correo)}</td>
                    <td>${GS.esc(student.telefono)}</td>
                    <td>
                        <button class="action-button" data-edit="${student.id || student._id}">
                            Editar
                        </button>
                        <button class="action-button danger" data-delete="${student.id || student._id}">
                            Eliminar
                        </button>
                    </td>
                </tr>
            `).join("")
            : `
                <tr>
                    <td colspan="5" class="empty-cell">
                        No se encontraron estudiantes.
                    </td>
                </tr>
            `;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const studentId = document.getElementById("student-id").value;
        const data = {
            nombre: document.getElementById("student-name").value.trim(),
            documento: document.getElementById("student-document").value.trim(),
            correo: document.getElementById("student-email").value.trim(),
            telefono: document.getElementById("student-phone").value.trim()
        };

        try {
            await GS.store.saveStudent(data, studentId || null);
            close();
            await render();

            GS.toast(
                studentId
                    ? "Estudiante actualizado."
                    : "Estudiante registrado."
            );
        } catch (error) {
            console.error(error);
            GS.toast(`No fue posible guardar el estudiante: ${error.message}`);
        }
    });

    tbody.addEventListener("click", async event => {
        const edit = event.target.dataset.edit;
        const del = event.target.dataset.delete;

        if (edit) {
            const students = await GS.store.getStudents();
            const student = students.find(item => (
                (item.id || item._id) === edit
            ));

            if (!student) return;

            document.getElementById("student-id").value = edit;
            document.getElementById("student-name").value = student.nombre || "";
            document.getElementById("student-document").value = student.documento || "";
            document.getElementById("student-email").value = student.correo || "";
            document.getElementById("student-phone").value = student.telefono || "";
            document.getElementById("student-modal-title").textContent = "Editar estudiante";

            open();
        }

        if (del && confirm("¿Seguro que deseas eliminar este estudiante?")) {
            try {
                await GS.store.deleteStudent(del);
                await render();

                GS.toast("Estudiante eliminado.");
            } catch (error) {
                console.error(error);
                GS.toast(`No fue posible eliminarlo: ${error.message}`);
            }
        }
    });

    search.addEventListener("input", render);

    render().catch(console.error);
})();