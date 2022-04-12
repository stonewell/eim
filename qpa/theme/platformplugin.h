#ifndef PLATFORMPLUGIN_H
#define PLATFORMPLUGIN_H

#include <qpa/qplatformtheme.h>
#include <qpa/qplatformthemeplugin.h>

#include "qeimplatformtheme.h"

class QEimPlatformThemePlugin : public QPlatformThemePlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QPlatformThemeFactoryInterface_iid FILE "qeimplatformtheme.json")
public:
    QEimPlatformThemePlugin(QObject *parent = 0);

    virtual QPlatformTheme *create(const QString &key, const QStringList &paramList);
};

#endif // PLATFORMPLUGIN_H
