(() => {
    const tbody = document.getElementById("pending-table");
    const search = document.getElementById("pending-search");

    if (!tbody) return;

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

        const pending = enrollments
            .filter(enrollment => !enrollment.pagado)
            .filter(enrollment => {
                const name =
                    enrollment.estudiante_nombre ||
                    names.get(String(enrollment.estudiante)) ||
                    enrollment.estudiante || "";

                return (
                    name + " " +
                    (enrollment.idioma || "") + " " +
                    (enrollment.idioma_nivel || "")
                ).toLowerCase().includes(term);
            });

        document.getElementById("pending-count").textContent = pending.length;
        document.getElementById("pending-label").textContent =
            `${pending.length} registro(s)`;

        document.getElementById("pending-total").textContent = GS.money(
            pending.reduce(
                (sum, enrollment) => sum + Number(enrollment.valor_curso || 0),
                0
            )
        );

        tbody.innerHTML = pending.length
            ? pending.map(enrollment => `
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
                    <td>
                        ${GS.esc(enrollment.idioma || "")} ·
                        ${GS.esc(enrollment.idioma_nivel || "")}
                    </td>
                    <td>${GS.money(enrollment.valor_curso)}</td>
                    <td>${GS.status(false)}</td>
                    <td>
                        <button
                            class="action-button"
                            data-paid="${enrollment.id || enrollment._id}"
                        >
                            Registrar pago
                        </button>
                    </td>
                </tr>
            `).join("")
            : `
                <tr>
                    <td colspan="5" class="empty-cell">
                        No hay pagos pendientes. ¡Excelente!
                    </td>
                </tr>
            `;
    }

    tbody.addEventListener("click", async event => {
        const id = event.target.dataset.paid;

        if (!id) return;

        try {
            await GS.store.updateEnrollment(id, { pagado: true });
            await render();

            GS.toast("Pago registrado correctamente.");
        } catch (error) {
            console.error(error);
            GS.toast(`No fue posible actualizar el pago: ${error.message}`);
        }
    });

    search.addEventListener("input", render);

    render().catch(console.error);
})();