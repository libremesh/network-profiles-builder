define Package/{{ community }}-{{ profile }}
  SECTION:=base
  CATEGORY:=Network Profiles
  TITLE:={{ profile }}
  URL:=https://github.com/libremesh/network-profiles/
  PKGARCH:=all
  DEPENDS:={{ packages }}
endef

define Package/{{ community }}-{{ profile }}/install
		$(INSTALL_DIR) $(1)/
		$(CP) -r ./{{ community }}/{{ profile }}/* $(1)/
endef

$(eval $(call BuildPackage,{{ community }}-{{ profile }}))
