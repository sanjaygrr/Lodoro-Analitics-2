// Funcionalidad para selección múltiple de órdenes y exportación de boletas
(function() {
    'use strict';
    
    function initOrderSelection() {
        console.log('Inicializando selección de órdenes');
        
        const selectAllCheckbox = document.getElementById('select-all-orders');
        const printSelectedBtn = document.getElementById('print-selected');
        
        if (!selectAllCheckbox || !printSelectedBtn) {
            console.error('No se encontraron elementos necesarios');
            return;
        }
        
        // Evento para seleccionar todas las órdenes
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            const orderCheckboxes = document.querySelectorAll('.order-checkbox');
            
            console.log(`Seleccionando todas: ${isChecked}, encontradas: ${orderCheckboxes.length}`);
            
            orderCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            
            updatePrintButton();
        });
        
        // Evento delegado para checkboxes individuales
        document.addEventListener('change', function(e) {
            if (e.target.classList.contains('order-checkbox')) {
                const orderCheckboxes = document.querySelectorAll('.order-checkbox');
                const checkedCount = document.querySelectorAll('.order-checkbox:checked').length;
                
                selectAllCheckbox.checked = checkedCount === orderCheckboxes.length;
                updatePrintButton();
            }
        });
        
        // Función para actualizar estado del botón
        function updatePrintButton() {
            const selectedCount = document.querySelectorAll('.order-checkbox:checked').length;
            printSelectedBtn.disabled = selectedCount === 0;
            console.log(`Órdenes seleccionadas: ${selectedCount}`);
        }
        
        // Inicializar estado del botón
        updatePrintButton();
    }
    
    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOrderSelection);
    } else {
        initOrderSelection();
    }
})();