(() => {
    const form = document.getElementById("enrollment-form");
    const tbody = document.getElementById("enrollments-table");

    if (!form) return;

    const studentSelect = document.getElementById("enrollment-student");
    const search = document.getElementById("enrollment-search");
    const filter = document.getElementById("enrollment-filter");

    async function loadStudents() {
        const students = await GS.store.getStudents();

        studentSelect.innerHTML =
            '<option value="">Selecciona un estudiante</option>' +
            students.map(student => `
                <option value="${GS.esc(student.id || student._id)}">
                    ${GS.esc(student.nombre)}
                </option>
            `).join("");
    }

    async function render() {
        const [enrollments, students] = await Promise.all([
            GS.store.getEnrollments(),
            GS.store.getStudents()
        ]);

        const names = new Map(
            students.map(student => [
                String(student.id || student._id),
                student.nombre
            ])
        );

        const term = search.value.toLowerCase();
        const state = filter.value;

        const list = enrollments.filter(enrollment => {
            const name =
                enrollment.estudiante_nombre ||
                names.get(String(enrollment.estudiante)) ||
                enrollment.estudiante || "";

            const matchesSearch = (
                name + " " +
                (enrollment.idioma || "") + " " +
                (enrollment.idioma_nivel || "")
            ).toLowerCase().includes(term);

            const matchesFilter =
                state === "todas" ||
                (state === "pagado" && enrollment.pagado) ||
                (state === "pendiente" && !enrollment.pagado);

            return matchesSearch && matchesFilter;
        });

        document.getElementById("enrollment-count").textContent =
            `${list.length} matrícula(s)`;

        tbody.innerHTML = list.length
            ? list.map(enrollment => `
                <tr>
                    <td>
                        <span class="student-name">
                            ${GS.esc(
                enrollment.estudiante_nombre ||
                names.get(String(enrollment.estudiante)) ||
                enrollment.estudiante ||
                "Sin nombre"
            )}
                        </span>
                    </td>
                    <td>${GS.esc(enrollment.idioma || "No especificado")}</td>
                    <td>${GS.esc(enrollment.idioma_nivel || "")}</td>
                    <td>${GS.money(enrollment.valor_curso)}</td>
                    <td>${GS.status(enrollment.pagado)}</td>
                    <td>
                        ${enrollment.pagado
                    ? '<span class="student-sub">Al día</span>'
                    : `
                                <button
                                    class="action-button"
                                    data-paid="${enrollment.id || enrollment._id}"
                                >
                                    Marcar pagado
                                </button>
                            `
                }
                        <button
                            class="action-button danger"
                            data-delete="${enrollment.id || enrollment._id}"
                        >
                            Eliminar
                        </button>
                    </td>
                </tr>
            `).join("")
            : `
                <tr>
                    <td colspan="6" class="empty-cell">
                        No hay matrículas para mostrar.
                    </td>
                </tr>
            `;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const studentId = studentSelect.value;
        const student = studentSelect.options[studentSelect.selectedIndex]?.text || "";

        const data = {
            estudiante: studentId,
            estudiante_nombre: student,
            idioma: document.getElementById("enrollment-language").value,
            idioma_nivel: document.getElementById("enrollment-level").value,
            valor_curso: Number(document.getElementById("enrollment-value").value),
            pagado: document.getElementById("enrollment-paid").checked
        };

        try {
            await GS.store.saveEnrollment(data);
            form.reset();
            await render();

            GS.toast("Matrícula registrada correctamente.");
        } catch (error) {
            console.error(error);
            GS.toast(`No fue posible registrar la matrícula: ${error.message}`);
        }
    });

    tbody.addEventListener("click", async event => {
        const paid = event.target.dataset.paid;
        const del = event.target.dataset.delete;

        if (paid) {
            try {
                const enrollments = await GS.store.getEnrollments();
                const item = enrollments.find(enrollment => (
                    (enrollment.id || enrollment._id) === paid
                ));

                if (item) {
                    await GS.store.updateEnrollment(paid, { pagado: true });
                    await render();

                    GS.toast("Pago actualizado.");
                }
            } catch (error) {
                console.error(error);
                GS.toast(`No fue posible actualizar el pago: ${error.message}`);
            }
        }

        if (del && confirm("¿Eliminar esta matrícula?")) {
            try {
                await GS.store.deleteEnrollment(del);
                await render();

                GS.toast("Matrícula eliminada.");
            } catch (error) {
                console.error(error);
                GS.toast(`No fue posible eliminar la matrícula: ${error.message}`);
            }
        }
    });

    search.addEventListener("input", render);
    filter.addEventListener("change", render);

    Promise.all([loadStudents(), render()]).catch(error => {
        console.error(error);
        GS.toast(`No fue posible cargar los datos: ${error.message}`);
    });
})();