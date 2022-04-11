#ifndef PLATFORMPLUGIN_H
#define PLATFORMPLUGIN_H

#include <qpa/qplatformtheme.h>
#include <qpa/qplatformthemeplugin.h>

#include "qeimplatformtheme.h"

class QEimPlatformThemePlugin : public QPlatformThemePlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "org.qt-project.Qt.QPA.QPlatformThemeFactoryInterface.5.1" FILE "qeimplatformtheme.json")
public:
    QEimPlatformThemePlugin(QObject *parent = 0);

    virtual QPlatformTheme *create(const QString &key, const QStringList &paramList);
};

#endif // PLATFORMPLUGIN_H
