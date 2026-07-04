import * as vscode from 'vscode';
import * as path from 'path';

let nexusTerminal: vscode.Terminal | undefined;

// El ejecutable de NexusDB va empaquetado dentro de la extensión (bin/NexusDB.exe),
// así que no depende de que el usuario tenga Python ni el código fuente del proyecto.
function getBundledExePath(context: vscode.ExtensionContext): string {
    return path.join(context.extensionPath, 'bin', 'NexusDB.exe');
}

export function activate(context: vscode.ExtensionContext) {
    const startCommand = vscode.commands.registerCommand('nexusdb.start', async () => {
        const exePath = getBundledExePath(context);

        if (!nexusTerminal || nexusTerminal.exitStatus !== undefined) {
            nexusTerminal = vscode.window.createTerminal({ name: 'NexusDB' });
        }

        nexusTerminal.show();
        // El operador '&' es obligatorio en PowerShell para ejecutar una ruta
        // entre comillas; sin él, PowerShell solo imprime el string.
        nexusTerminal.sendText(`& "${exePath}"`);
    });

    context.subscriptions.push(startCommand);
}

export function deactivate() {
    nexusTerminal = undefined;
}
