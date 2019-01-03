#pragma once

#include "Extender.h"

class KeyBindingExtension : public Extension {
private:
	KeyBindingExtension() : m_Host(nullptr) {} // Singleton
	KeyBindingExtension(const KeyBindingExtension &) = delete; // Disable copy ctor
	void operator=(const KeyBindingExtension &) = delete;    // Disable operator=

public:
	static KeyBindingExtension &Instance();

	// Implement the Extension interface
	virtual bool Initialise(ExtensionAPI *host_) override;
	virtual bool Finalise() override;
	virtual bool Clear() override;
	virtual bool Load(const char *filename) override;

	virtual bool OnKey(int, int) override;
private:
	ExtensionAPI * m_Host;
    std::string m_BindingConfig;

    bool LoadBindingConfig(const std::string & config);
    bool LoadFile(const std::string & file_path);
};
